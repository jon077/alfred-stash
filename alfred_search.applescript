--Aaron Bach
--LastPass Vault Manager
on run argv
	
	set command to argv as text
	
	tell application "Alfred 2" to search command
	
end run