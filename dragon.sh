for data in "blackscholes" "bodytrack" "fluidanimate";
do 
    for cache in 1024 8092 32768; 
    do
        for assoc in 1 2 4;
        do
            for block in 8 32 128;
            do
                echo $data $cache $assoc $block
                ~/Downloads/pypy2-v5.6.0-osx64/bin/pypy simulator.py dragon $data $cache $assoc $block
            done
        done
    done
done