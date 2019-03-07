 import-module servermanager 
 Add-WindowsFeature -Name "RSAT-AD-PowerShell" -IncludeAllSubFeature
 Get-ADUser -Filter * -Properties DisplayName, EmailAddress, Title | select DisplayName, EmailAddress, Title | Export-CSV "Email_Addresses.csv"
