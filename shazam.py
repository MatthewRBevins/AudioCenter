import asyncio
from shazamio import Shazam, Serialize
import time


async def main():
    shazam = Shazam()
    song = input("File Name: ")
    
    start = time.time()
    out = await shazam.recognize_song(song)
    #print(out)

    serialized = Serialize.full_track(out)
    print(serialized)
    end = time.time()
    print(end-start)
    


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())