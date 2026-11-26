# eNuts Asset & Directory Inventory
*Auto-generated on: 2026-11-26 03:47:33 UTC*

## Current Directory Structure

```text
eNuts/
├── .bin/
│   └── scrcpy-server.jar
├── .clinerules/
│   ├── rules/
│   │   ├── CodingStyle.md
│   │   ├── Documentation.md
│   │   └── NamingConventions.md
│   └── templates/
│       └── documentTemplates.md
├── .gitignore
├── .kilocode/
│   └── .gitignore
├── .pytest_cache/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v/
│       └── cache/
│           ├── lastfailed
│           └── nodeids
├── .scripts/
│   └── updateInventory.py
├── .test/
│   ├── README.md
│   └── fixtures/
│       ├── ipc/
│       │   └── payloads.py
│       └── policy/
│           ├── builders.py
│           └── seeds.py
├── README.md
├── assets/
│   ├── gameInfo.json
│   ├── icons/
│   │   ├── KGRecorder.png
│   │   ├── annotation.png
│   │   ├── collapse.png
│   │   ├── dashboard.png
│   │   ├── expand.png
│   │   ├── logo.png
│   │   ├── settings.png
│   │   └── tools.png
│   ├── logo.png
│   ├── names.json
│   ├── names_categorized.json
│   └── templates/
│       ├── MiniMode.png
│       └── NormalMode.png
├── config/
│   ├── .fff
│   ├── eNuts/
│   │   └── appconfig.json
│   ├── emitter/
│   │   └── sizeBitrateMap.py
│   └── themes/
│       ├── dark
│       ├── dracula
│       ├── ironman
│       ├── light
│       ├── material
│       ├── options/
│       │   └── dark/
│       │       ├── Animation.json
│       │       └── SideBar.json
│       └── qss/
│           ├── main.css
│           ├── page.css
│           └── sideBar.css
├── src/
│   ├── TEST/
│   │   └── smoke/
│   │       ├── emitters/
│   │       └── ipc/
│   │           └── processHost.py
│   ├── __monkeyPatch.py
│   ├── eNuts/
│   │   ├── .ff
│   │   ├── UI/
│   │   │   ├── .ff
│   │   │   ├── navigation/
│   │   │   │   ├── __navigation.py
│   │   │   │   ├── __pageKeys.py
│   │   │   │   └── __sideBarMenuBuilder.py
│   │   │   ├── pages/
│   │   │   │   ├── __annotator.py
│   │   │   │   ├── __devicePage.py
│   │   │   │   ├── __helper.py
│   │   │   │   ├── __kgRecorder.py
│   │   │   │   ├── __pageKeys.py
│   │   │   │   ├── __playbackBase.py
│   │   │   │   ├── __recorderState.py
│   │   │   │   └── __smokePages.py
│   │   │   ├── widgets/
│   │   │   │   ├── CaptureGLImage/
│   │   │   │   │   └── __captureGLImage.py
│   │   │   │   ├── DeviceCard/
│   │   │   │   │   └── __deviceCard.py
│   │   │   │   └── MediaPlayer/
│   │   │   │       └── __mediaPlayer.py
│   │   ├── application/
│   │   │   ├── workspace/
│   │   │   │   └── __workSpace.py
│   │   │   └── __application.py
│   │   ├── apps/
│   │   │   └── main.py
│   │   ├── services/
│   │   │   ├── clients/
│   │   │   │   ├── deviceManager/
│   │   │   │   │   ├── __deviceDiscovery.py
│   │   │   │   │   ├── __deviceManager.py
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   └── message/
│   │   │   │   │       └── __init__.py
│   │   │   │   └── __manager.py
│   │   │   └── recorder/
│   │   │       └── __recorder.py
│   │   ├── types/
│   │   │   └── interface/
│   │   │       └── services/
│   │   │           └── __init__.py
│   │   └── __shell.py
│   ├── fluxCore/
│   │   ├── device/
│   │   │   ├── SCRCPYDevice.py
│   │   │   └── __init__.py
│   │   ├── emitters/
│   │   │   └── __SCRCPYEmitter.py
│   │   ├── stream/
│   │   │   ├── deviceStream/
│   │   │   │   └── __deviceStream.py
│   │   │   ├── frameRing/
│   │   │   │   └── __frameRing.py
│   │   │   └── frameSlot/
│   │   │       └── __frameSlot.py
│   │   ├── types/
│   │   │   └── interface/
│   │   │       └── device/
│   │   │           └── __init__.py
│   │   └── utilities/
│   │       └── scrcpy/
│   │           └── __scrcpy.py
│   ├── jAGFx/
│   │   ├── IPC/
│   │   │   ├── client/
│   │   │   │   └── __client.py
│   │   │   ├── message/
│   │   │   │   └── __init__.py
│   │   │   ├── workerBase/
│   │   │   │   └── __workerBase.py
│   │   │   ├── __processHost.py
│   │   │   └── __workers.py
│   │   ├── logging/
│   │   │   ├── formatters/
│   │   │   │   └── __defaultFormatter.py
│   │   │   ├── __init__.py
│   │   │   ├── __log.py
│   │   │   ├── __logging.py
│   │   │   └── __utilities.py
│   │   ├── services/
│   │   │   └── __asyncProcess.py
│   │   └── types/
│   │       └── interface/
│   │           └── communication/
│   │               ├── messages/
│   │               │   └── __init__.py
│   │               └── __init__.py
│   ├── jAGQt/
│   │   ├── animations/
│   │   │   └── __animationBase.py
│   │   └── widgets/
│   │       ├── SideBar/
│   │       │   ├── components/
│   │       │   │   └── __sideBarHeader.py
│   │       │   ├── menu/
│   │       │   │   ├── __sideBarMenu.py
│   │       │   │   └── __sideBarMenuItem.py
│   │       │   └── __sideBar.py
│   │       └── icon/
│   │           └── __stateFullIcon.py
│   ├── main.py
│   └── utilities/
│       ├── __frame.py
│       ├── __init__.py
│       ├── asyncADB/
│       │   └── __asyncADB.py
│       └── io/
│           └── __io.py
├── typings/
│   └── __builtins__.pyi
└── update_inventory.yml
```

## Python Package Inventory

(Inventory regenerated after converting deviceManager TRACE → VERBOSE logging.)
