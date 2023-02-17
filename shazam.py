import asyncio
from shazamio import Shazam, Serialize


async def main():
    shazam = Shazam()
    song = input("File Name: ")
    out = await shazam.recognize_song(song)
    #print(out)

    serialized = Serialize.full_track(out)
    print(serialized)


loop = asyncio.get_event_loop_policy().get_event_loop()
loop.run_until_complete(main())