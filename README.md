# honkai-cg-extractor
extracts Honkai's CGs into playable video files

## Requirements:
### Included in release package:
You don't need to download these since I will include them in the release package because licenses allow me to.
- [OpenedFilesView](https://www.nirsoft.net/utils/opened_files_view.html)  
- [selurvedu's fork of UsmDemuxer](https://github.com/selurvedu/UsmDemuxer)  
### Download yourself:
- [.NET 5.0 Runtime](https://dotnet.microsoft.com/en-us/download/dotnet/thank-you/runtime-5.0.17-windows-x64-installer)

## How To Use:  
Simply run it, tell it if you want audio or not, and you will have your video files in the CGs subfolder :D

### CLI Usage
```
usage: HonkaiCGExtractor [-h] [-a] [-s] [-na] [-ns] [FILES ...]

positional arguments:
  FILES            .usm files to be converted. will detect any currently playing CGs if not specified

optional arguments:
  -h, --help       show this help message and exit
  -a, --audio      will extract audio without asking
  -s, --subs       will extract subtitles without asking
  -na, --no-audio  will skip audio extraction without asking
  -ns, --no-subs   will skip subtitles extraction without asking
```
