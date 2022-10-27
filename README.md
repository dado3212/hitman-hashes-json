# Hitman Hashes in JSON
A JSON dump of the hashes in Hitman. You can build it yourself with `python3 build_json.py`, but the easiest way is to just download the latest release file.

Here's a sample format that it's in:

```
"0004C5883B5D9CC5": {
    "name": "[modules:/zrenderdestinationtextureentity.class].pc_entitytype",
    "type": "CPPT",
    "depends": [
        "008E76B1A30210C7"
    ],
    "chunks": [
        "0",
        "0.1"
    ],
    "correct_name": true,
    "hex_strings": [
        "TArray<ZEntityReferenceI",
        ".ERoomBehaviour"
    ]
},
```

LZ4 DLL extracted from the download for Windows from this release - https://github.com/lz4/lz4/releases/tag/v1.9.4. The DLL loading unfortunately
makes this likely very very difficult to run on a computer, that's not mine. Sorry, good luck, I'll accept any pull request that fixes this but after
spending an hour bashing my head into old Python installs, a working version takes priority.
 
## Thanks

This relies heavily on [PRKG-Tool](https://notex.app/rpkg/) both directly (the hash_list.txt file) and indirectly (I ported some of the code to Python, relying heavily on the C++ logic). A HUGE thanks to the author of the original repo, available at https://github.com/glacier-modding/RPKG-Tool.

This code is heavily cribbed from my other repo, https://github.com/dado3212/hitman-art/.
 
# Licenses

All rights to the Hitman 3 game held by IOI.

---

RPKG
Copyright (c) 2020+, REDACTED
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice, this
  list of conditions and the following disclaimer in the documentation and/or
  other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
