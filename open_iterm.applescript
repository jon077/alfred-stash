--http://www.alfredforum.com/topic/1180-extra-tab-is-open-when-using-iterm2/
on run argv
	
	set command to argv as text
	
	tell application "System Events"
		set _wasRunning to exists (processes where name is "iTerm")
	end tell
	
	tell application "iTerm"
		activate
		
		if not _wasRunning then
			set _session to current session of current terminal
		else
			set _term to current terminal
			tell _term
				launch session "Default"
				set _session to current session
			end tell
		end if
		
		tell _session
			write text command
		end tell
	end tell
end run