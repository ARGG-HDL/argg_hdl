 function  replace-string($old_value,$new_value){
 
    dir *.py -Recurse | foreach{ 
        Write-Output $_.BaseName
        $a = Get-Content $_ ; 
        if( $a -like "*$old_value*"){  
            $b =  $a -replace "$old_value","$new_value";  
            Set-Content -Value $b -Path $_ 
        }
    }
 }