# NSworkaround
NSbuilder NS block scheme workaround.

This is a workaround for nsbuilder program. Thanks to this script you can write a code that can be converted into ns builder file. 
For example, create a file max.nss :
```
begin "Autor" "Dwie funkcje"
echo 'Please '

get a b c
x:=0

if b > a and b > c
    x:=c
    c:=b
    b:=x
fi

if a > c and a > b
    x:=c
    c:=a
    a:=x
fi

if a > b
    x:=a
    a:=b
    b:=a
fi

```

Then complile the file.
    ```python parse.py max.nssc  > max.nss.```
Now you can open the block scheme:
    ``` nsbuilder max.mss```
    
<img src="https://i.imgur.com/5FwxNkX.png"></img>
