use AppleScript version "2.4"
use scripting additions

set projectRoot to "/Users/leonardo/phd-thesis-animations"
set qualityFolder to "480p15"
set outputDir to projectRoot & "/media/keynote"
set deckBaseName to "phd-defence-presentation"
set slideWidth to 1920
set slideHeight to 1080

on ensureDirectoryExists(posixPath)
	do shell script ("/bin/mkdir -p " & quoted form of posixPath)
end ensureDirectoryExists

on existingDirectoryOrFail(posixPath, labelText)
	try
		do shell script ("/bin/test -d " & quoted form of posixPath)
	on error
		error labelText & " not found: " & posixPath
	end try
end existingDirectoryOrFail

on timestampString()
	return do shell script "/bin/date +%Y%m%d_%H%M%S"
end timestampString

on waitForFile(posixPath, timeoutSeconds)
	repeat (timeoutSeconds * 10) times
		try
			do shell script ("/bin/test -f " & quoted form of posixPath)
			return true
		on error
			delay 0.1
		end try
	end repeat
	return false
end waitForFile

on findVideos(projectRoot, qualityFolder)
	set study1Dir to projectRoot & "/media/videos/study1/" & qualityFolder
	set study2Dir to projectRoot & "/media/videos/study2/" & qualityFolder
	my existingDirectoryOrFail(study1Dir, "Study 1 video folder")
	my existingDirectoryOrFail(study2Dir, "Study 2 video folder")
	
	set shellCommand to "/usr/bin/find " & quoted form of study1Dir & " " & quoted form of study2Dir & " -maxdepth 1 -type f -name '*.mp4' | /usr/bin/sort"
	set videoListText to do shell script shellCommand
	if videoListText is "" then error "No MP4 videos found in " & qualityFolder
	return paragraphs of videoListText
end findVideos

on blankLayoutForDocument(docRef)
	tell application "Keynote"
		repeat with aLayout in slide layouts of docRef
			if (name of aLayout is "Blank") then return aLayout
		end repeat
		return first slide layout of docRef
	end tell
end blankLayoutForDocument

on prepareSlide(aSlide, blankLayout)
	tell application "Keynote"
		tell aSlide
			set base layout to blankLayout
			set title showing to false
			set body showing to false
		end tell
	end tell
end prepareSlide

on addMovieToSlide(aSlide, videoPath, slideWidth, slideHeight)
	set movieFileAlias to (POSIX file videoPath) as alias
	tell application "Keynote"
		tell aSlide
			-- In current Keynote versions, movies are imported via the image class.
			-- The returned object reference is a movie item once the media is placed.
			set movieRef to make new image with properties {file:movieFileAlias}
			set position of movieRef to {0, 0}
			set width of movieRef to slideWidth
			set height of movieRef to slideHeight
			set movie volume of movieRef to 100
		end tell
	end tell
end addMovieToSlide

on guiSaveDocument(outputName, saveDir)
	tell application "Keynote" to activate
	delay 0.6
	
	tell application "System Events"
		tell process "Keynote"
			set frontmost to true
			keystroke "s" using command down
			
			repeat 50 times
				if exists sheet 1 of window 1 then exit repeat
				delay 0.2
			end repeat
			if not (exists sheet 1 of window 1) then error "Keynote Save dialog did not appear."
			
			keystroke "G" using {command down, shift down}
			repeat 30 times
				if exists sheet 1 of sheet 1 of window 1 then exit repeat
				delay 0.1
			end repeat
			if not (exists sheet 1 of sheet 1 of window 1) then error "Go to Folder sheet did not appear."
			
			keystroke saveDir
			key code 36
			delay 0.5
			
			keystroke "a" using command down
			keystroke outputName
			delay 0.2
			key code 36
			delay 0.8
			
			if exists sheet 1 of window 1 then
				try
					click button "Replace" of sheet 1 of window 1
				on error
					key code 36
				end try
			end if
		end tell
	end tell
end guiSaveDocument

set ts to my timestampString()
set outputName to deckBaseName & "_" & ts & ".key"
set outputPath to outputDir & "/" & outputName

my ensureDirectoryExists(outputDir)
set videoPaths to my findVideos(projectRoot, qualityFolder)

tell application "Keynote"
	activate
	
	set docRef to make new document
	set width of docRef to slideWidth
	set height of docRef to slideHeight
	
	set blankLayout to my blankLayoutForDocument(docRef)
	
	set slideIndex to 0
	repeat with videoPath in videoPaths
		set slideIndex to slideIndex + 1
		if slideIndex is 1 then
			set slideRef to first slide of docRef
		else
			set slideRef to make new slide at end of slides of docRef with properties {base layout:blankLayout}
		end if
		
		my prepareSlide(slideRef, blankLayout)
		my addMovieToSlide(slideRef, (contents of videoPath), slideWidth, slideHeight)
	end repeat
	
	my guiSaveDocument(outputName, outputDir)
	if my waitForFile(outputPath, 60) is false then error "Keynote did not produce the saved file at " & outputPath
	
	display dialog "Created " & outputName & " with " & (count of videoPaths) & " slides at " & outputPath buttons {"OK"} default button "OK"
end tell
