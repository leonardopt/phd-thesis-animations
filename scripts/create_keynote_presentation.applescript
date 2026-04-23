use AppleScript version "2.4"
use framework "Foundation"
use scripting additions

-- Usage:
--   osascript scripts/create_keynote_presentation.applescript
--   osascript scripts/create_keynote_presentation.applescript -qh
--   osascript scripts/create_keynote_presentation.applescript --quality-folder 1080p60

property projectRoot : "/Users/leonardo/phd-thesis-animations"
property manifestPath : "/Users/leonardo/phd-thesis-animations/assets/presentation_deck.toml"

-- Ensure a destination directory exists before Keynote or export helpers write into it.
-- posixPath: absolute POSIX path string.
on ensureDirectoryExists(posixPath)
	set fileManager to current application's NSFileManager's defaultManager()
	set directoryURL to current application's NSURL's fileURLWithPath:posixPath
	set {created, createError} to fileManager's createDirectoryAtURL:directoryURL withIntermediateDirectories:true attributes:(missing value) |error|:(reference)
	if (created as boolean) is false then error ((createError's localizedDescription()) as text)
end ensureDirectoryExists

-- Fail early when a manifest or media path that the deck depends on is missing.
-- Returns no value; raises an AppleScript error with the provided label.
on existingFileOrFail(posixPath, labelText)
	set fileManager to current application's NSFileManager's defaultManager()
	if (fileManager's fileExistsAtPath:posixPath) as boolean is false then error labelText & " not found: " & posixPath
end existingFileOrFail

-- Return a filesystem-safe timestamp for output deck naming.
on timestampString()
	set formatter to current application's NSDateFormatter's alloc()'s init()
	formatter's setDateFormat:"yyyyMMdd_HHmmss"
	return (formatter's stringFromDate:(current application's NSDate's |date|())) as text
end timestampString

-- Poll for a file to appear after Keynote export completes.
-- Returns true when the file exists within timeoutSeconds, else false.
on waitForFile(posixPath, timeoutSeconds)
	set fileManager to current application's NSFileManager's defaultManager()
	repeat (timeoutSeconds * 10) times
		if (fileManager's fileExistsAtPath:posixPath) as boolean then return true
		delay 0.1
	end repeat
	return false
end waitForFile

-- Run a subprocess inside the repository and return stdout as text.
-- executablePath: tool to launch. argumentList: argv list. workingDirectory: cwd.
on runCommandInDirectory(executablePath, argumentList, workingDirectory)
	set task to current application's NSTask's alloc()'s init()
	set stdoutPipe to current application's NSPipe's pipe()
	set stderrPipe to current application's NSPipe's pipe()
	
	task's setExecutableURL:(current application's NSURL's fileURLWithPath:executablePath)
	task's setArguments:argumentList
	task's setCurrentDirectoryURL:(current application's NSURL's fileURLWithPath:workingDirectory)
	task's setStandardOutput:stdoutPipe
	task's setStandardError:stderrPipe
	
	set {launched, launchError} to task's launchAndReturnError:(reference)
	if (launched as boolean) is false then error ((launchError's localizedDescription()) as text)
	
	task's waitUntilExit()
	
	set stdoutData to stdoutPipe's fileHandleForReading()'s readDataToEndOfFile()
	set stderrData to stderrPipe's fileHandleForReading()'s readDataToEndOfFile()
	set stdoutText to (current application's NSString's alloc()'s initWithData:stdoutData encoding:(current application's NSUTF8StringEncoding)) as text
	set stderrText to (current application's NSString's alloc()'s initWithData:stderrData encoding:(current application's NSUTF8StringEncoding)) as text
	
	if (task's terminationStatus()) as integer is not 0 then
		if stderrText is "" then set stderrText to "Command failed with exit status " & ((task's terminationStatus()) as text)
		error stderrText
	end if
		return stdoutText
end runCommandInDirectory

-- Resolve the requested Manim quality folder from CLI arguments.
-- Accepts either the short quality flag or an explicit --quality-folder value.
on qualityFolderFromArgs(argv)
	if (count of argv) is 0 then return "480p15"
	
	set currentArg to (item 1 of argv) as text
	if currentArg is "--quality-folder" then
		if (count of argv) < 2 then error "Missing folder name after --quality-folder."
		return my normalizeQualityValue((item 2 of argv) as text)
	else if currentArg starts with "--quality-folder=" then
		return my normalizeQualityValue(text ((length of "--quality-folder=") + 1) thru -1 of currentArg)
	else
		return my normalizeQualityValue(currentArg)
	end if
end qualityFolderFromArgs

-- Normalize supported quality aliases onto the folder names used in media/videos.
on normalizeQualityValue(rawValue)
	set trimmedValue to rawValue as text
	if trimmedValue is "" then return "480p15"
	
	if trimmedValue is "-ql" or trimmedValue is "ql" or trimmedValue is "480p15" then return "480p15"
	if trimmedValue is "-qm" or trimmedValue is "qm" or trimmedValue is "720p30" then return "720p30"
	if trimmedValue is "-qh" or trimmedValue is "qh" or trimmedValue is "1080p60" then return "1080p60"
	if trimmedValue is "-qk" or trimmedValue is "qk" or trimmedValue is "2160p60" then return "2160p60"
	
	error "Unsupported quality argument: " & trimmedValue & ". Use -ql, -qm, -qh, -qk, or a folder like 480p15."
end normalizeQualityValue

-- Load the serialized deck spec produced by the Python manifest flattener.
-- Returns {outputDir, deckBaseName, slideWidth, slideHeight, slideSpecs}.
on loadDeckSpec(projectRoot, manifestPath, qualityFolder)
	my existingFileOrFail(manifestPath, "Presentation manifest")
	try
		set rawSpec to my runCommandInDirectory("/usr/bin/python3", {"scripts/presentation_manifest.py", "--manifest", manifestPath, "--project-root", projectRoot, "--quality-dir", qualityFolder}, projectRoot)
	on error errMsg number errNum
		error "Unable to load presentation manifest. " & errMsg number errNum
	end try
	return my parseDeckSpec(rawSpec)
end loadDeckSpec

-- Decode the manifest transport format emitted by presentation_manifest.py.
-- rawSpec uses record separator 30 and field separator 31.
on parseDeckSpec(rawSpec)
	set recSep to character id 30
	set fldSep to character id 31
	set previousTIDs to AppleScript's text item delimiters
	try
		set AppleScript's text item delimiters to recSep
		set rawRecords to text items of rawSpec
		if (count of rawRecords) < 2 then error "Presentation manifest did not contain any slide records."
		
		set AppleScript's text item delimiters to fldSep
		set deckFields to text items of item 1 of rawRecords
		if (count of deckFields) < 5 then error "Malformed deck metadata record."
		if item 1 of deckFields is not "deck" then error "First manifest record was not deck metadata."
		
		set outputDir to item 2 of deckFields
		set deckBaseName to item 3 of deckFields
		set slideWidth to (item 4 of deckFields) as integer
		set slideHeight to (item 5 of deckFields) as integer
		
		set slideSpecs to {}
		repeat with rawRecord in items 2 thru -1 of rawRecords
			set slideFields to text items of (contents of rawRecord)
			if (count of slideFields) < 7 then error "Malformed slide record in presentation manifest."
			if item 1 of slideFields is not "slide" then error "Encountered unexpected manifest record."
			set end of slideSpecs to {item 2 of slideFields, item 3 of slideFields, item 4 of slideFields, item 5 of slideFields, item 6 of slideFields, item 7 of slideFields}
		end repeat
	on error errMsg number errNum
		set AppleScript's text item delimiters to previousTIDs
		error errMsg number errNum
	end try
	set AppleScript's text item delimiters to previousTIDs
	return {outputDir, deckBaseName, slideWidth, slideHeight, slideSpecs}
end parseDeckSpec

-- Pick the first matching Keynote slide layout name, or fall back if none exist.
on slideLayoutNamed(docRef, preferredNames, fallbackLayout)
	tell application "Keynote"
		repeat with preferredName in preferredNames
			repeat with aLayout in (every slide layout of docRef)
				if (name of aLayout is (contents of preferredName)) then return aLayout
			end repeat
		end repeat
	end tell
	return fallbackLayout
end slideLayoutNamed

-- Apply the requested layout and title/body visibility to one slide shell.
on prepareSlide(aSlide, targetLayout, showTitle, showBody)
	tell application "Keynote"
		tell aSlide
			set base layout to targetLayout
			set title showing to showTitle
			set body showing to showBody
		end tell
	end tell
end prepareSlide

-- Merge subtitle and body text into the single Keynote body field when needed.
on combinedBodyText(subtitleText, bodyText)
	if subtitleText is not "" and bodyText is not "" then
		return subtitleText & return & return & bodyText
	else if bodyText is not "" then
		return bodyText
	else
		return subtitleText
	end if
end combinedBodyText

-- Populate a slide's text placeholders and presenter notes when present.
on setSlideText(aSlide, titleText, bodyText, notesText)
	tell application "Keynote"
		tell aSlide
			try
				if titleText is not "" then
					set title showing to true
					set object text of default title item to titleText
				else
					set title showing to false
				end if
			end try
			
			try
				if bodyText is not "" then
					set body showing to true
					set object text of default body item to bodyText
				else
					set body showing to false
				end if
			end try
			
			if notesText is not "" then set presenter notes to notesText
			end tell
		end tell
end setSlideText

-- Reject any media path that is not a numbered section clip. The manifest
-- performs the same validation; this second check keeps the deck builder from
-- silently drifting if a malformed slide record ever reaches AppleScript.
on assertSectionVideoPath(videoPath)
	if videoPath does not contain "/sections/" then error "Deck videos must come from a /sections/ directory: " & videoPath
	if videoPath ends with "_autocreated.mp4" then error "Deck videos must not use autocreated section clips: " & videoPath
end assertSectionVideoPath

-- Add one full-slide movie asset to a blank-layout slide.
on addMovieToSlide(aSlide, videoPath, slideWidth, slideHeight)
	my assertSectionVideoPath(videoPath)
	set movieFileAlias to (POSIX file videoPath) as alias
	tell application "Keynote"
		tell aSlide
			set movieRef to make new image with properties {file:movieFileAlias}
			set position of movieRef to {0, 0}
			set width of movieRef to slideWidth
			set height of movieRef to slideHeight
			set movie volume of movieRef to 100
		end tell
	end tell
end addMovieToSlide

-- Add one full-slide image or PDF preview asset to a blank-layout slide.
on addImageToSlide(aSlide, imagePath, slideWidth, slideHeight)
	set imageFileAlias to (POSIX file imagePath) as alias
	tell application "Keynote"
		tell aSlide
			set imageRef to make new image with properties {file:imageFileAlias}
			set position of imageRef to {0, 0}
			set width of imageRef to slideWidth
			set height of imageRef to slideHeight
		end tell
	end tell
end addImageToSlide

-- Populate one slide from a normalized manifest tuple.
-- slideSpec order is {slideType, mediaPath, titleText, subtitleText, bodyText, notesText}.
-- Text-oriented records leave mediaPath empty; media-oriented records may leave
-- the text fields blank and still pass presenter notes through unchanged.
-- Each branch picks the narrowest Keynote layout contract that matches the
-- manifest semantics so the AppleScript, rather than the manifest, owns the
-- presentation-specific layout policy.
on populateSlide(aSlide, slideSpec, blankLayout, titleLayout, sectionLayout, titleOnlyLayout, textBulletsLayout, slideWidth, slideHeight)
	set slideType to item 1 of slideSpec
	set mediaPath to item 2 of slideSpec
	set titleText to item 3 of slideSpec
	set subtitleText to item 4 of slideSpec
	set bodyText to item 5 of slideSpec
	set notesText to item 6 of slideSpec
	if slideType is "video" then
		-- Media slides occupy the entire slide canvas and do not use text placeholders.
		my prepareSlide(aSlide, blankLayout, false, false)
		my addMovieToSlide(aSlide, mediaPath, slideWidth, slideHeight)
		if notesText is not "" then tell application "Keynote" to set presenter notes of aSlide to notesText
		return
	end if
	if slideType is "image" or slideType is "pdf" then
		-- Image and PDF slides share the same blank full-slide treatment as videos.
		my prepareSlide(aSlide, blankLayout, false, false)
		my addImageToSlide(aSlide, mediaPath, slideWidth, slideHeight)
		if notesText is not "" then tell application "Keynote" to set presenter notes of aSlide to notesText
		return
	end if
	if slideType is "title" then
		-- Title slides keep both placeholders visible because subtitle and body
		-- content are merged into the single Keynote body field.
		my prepareSlide(aSlide, titleLayout, true, true)
		my setSlideText(aSlide, titleText, my combinedBodyText(subtitleText, bodyText), notesText)
		return
	end if
	if slideType is "section" then
		-- Section slides reuse the same merged-text contract but prefer the deck's
		-- section layout when that template is available.
		my prepareSlide(aSlide, sectionLayout, true, true)
		my setSlideText(aSlide, titleText, my combinedBodyText(subtitleText, bodyText), notesText)
		return
	end if
	if slideType is "text" then
		-- Text slides switch between a title-only and bullets layout depending on whether body content exists.
		set effectiveBodyText to my combinedBodyText(subtitleText, bodyText)
		if effectiveBodyText is "" then
			my prepareSlide(aSlide, titleOnlyLayout, true, false)
		else
			my prepareSlide(aSlide, textBulletsLayout, true, true)
		end if
		my setSlideText(aSlide, titleText, effectiveBodyText, notesText)
		return
	end if
	-- Reject unknown slide types here so the manifest schema and AppleScript
	-- dispatch table stay in sync instead of silently choosing a bad layout.
	error "Unsupported slide type: " & slideType
end populateSlide

-- Build a new Keynote document from the normalized manifest and export it.
-- argv accepts the same quality selection forms as the render shell scripts.
on run argv
	set qualityFolder to my qualityFolderFromArgs(argv)
	set {outputDir, deckBaseName, slideWidth, slideHeight, slideSpecs} to my loadDeckSpec(projectRoot, manifestPath, qualityFolder)
	set ts to my timestampString()
	set outputName to deckBaseName & "_" & ts & ".key"
	set outputPath to outputDir & "/" & outputName
	
	my ensureDirectoryExists(outputDir)
	
	tell application "Keynote"
		activate
		
		set docRef to make new document
		set width of docRef to slideWidth
		set height of docRef to slideHeight
		
		set blankLayout to my slideLayoutNamed(docRef, {"Blank"}, first slide layout of docRef)
		set titleLayout to my slideLayoutNamed(docRef, {"Title"}, blankLayout)
		set sectionLayout to my slideLayoutNamed(docRef, {"Section", "Title"}, titleLayout)
		set titleOnlyLayout to my slideLayoutNamed(docRef, {"Title Only", "Title"}, titleLayout)
		set textBulletsLayout to my slideLayoutNamed(docRef, {"Title & Bullets", "Bullets", "Title"}, titleOnlyLayout)
		
		set slideIndex to 0
		repeat with slideSpec in slideSpecs
			set slideIndex to slideIndex + 1
			if slideIndex is 1 then
				set slideRef to first slide of docRef
			else
				set slideRef to make new slide at end of slides of docRef with properties {base layout:blankLayout}
			end if
			my populateSlide(slideRef, slideSpec, blankLayout, titleLayout, sectionLayout, titleOnlyLayout, textBulletsLayout, slideWidth, slideHeight)
		end repeat
		
		export docRef to (POSIX file outputPath) as Keynote 09
		close docRef saving no
	end tell
	
	if my waitForFile(outputPath, 120) is false then error "Keynote did not produce the saved file at " & outputPath
	try
		-- Rewrite Keynote's stored font names so deck text uses Computer Modern.
		my runCommandInDirectory("/usr/bin/python3", {"scripts/force_keynote_cmu_font.py", "--presentation-file", outputPath}, projectRoot)
	on error errMsg number errNum
		error "Keynote export succeeded, but CMU font post-processing failed. " & errMsg number errNum
	end try
	
	display dialog "Created " & outputName & " using video folder " & qualityFolder & " with " & (count of slideSpecs) & " slides at " & outputPath buttons {"OK"} default button "OK"
	return outputPath
end run
