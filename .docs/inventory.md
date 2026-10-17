# eNuts Asset & Directory Inventory
*Auto-generated on: 2026-10-17 08:47:36 UTC*

## Current Directory Structure

```text
eNuts/
├── .bin/
│   └── scrcpy-server.jar
├── .gitignore
├── .kilocode/
│   ├── .gitignore
│   ├── rules/
│   │   ├── CodingStyle.md
│   │   ├── Documentation.md
│   │   └── NamingConventions.md
│   └── templates/
│       └── documentTemplates.md
├── .scripts/
│   └── updateInventory.py
├── README.md
├── assets/
│   ├── gameInfo.json
│   ├── icons/
│   │   ├── collapse.png
│   │   ├── expand.png
│   │   └── logo.png
│   ├── logo copy.png
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
│   └── themes/
│       ├── dark/
│       │   ├── main.css
│       │   ├── options/
│       │   │   ├── Animation.json
│       │   │   └── SideBar.json
│       │   └── palette
│       ├── dracula/
│       │   ├── main.css
│       │   └── palette
│       ├── ironman/
│       │   ├── main.css
│       │   └── palette
│       ├── light/
│       │   ├── main.css
│       │   └── palette
│       ├── material/
│       │   ├── main.css
│       │   └── palette
│       └── superman/
├── src/
│   ├── __monkeyPatch.py
│   ├── eNuts/
│   │   ├── .ff
│   │   ├── UI/
│   │   │   ├── .ff
│   │   │   ├── navigation/
│   │   │   │   └── __sideBarMenuBuilder.py
│   │   │   ├── widgets/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── dashboard/
│   │   │   │   │   ├── recorder/
│   │   │   │   │   │   └── __recorderPage.py
│   │   │   │   │   └── settings/
│   │   │   │   │       └── __settingsPage.py
│   │   │   │   ├── spinners/
│   │   │   │   │   ├── __evolvingNeuralBrain.py
│   │   │   │   │   ├── __evolvingNeuralOrb.py
│   │   │   │   │   └── __revolvingNeuralOrb.py
│   │   │   │   └── streamer/
│   │   │   └── windows/
│   │   │       └── __mainWindow.py
│   │   ├── application/
│   │   │   ├── __applicationInformation.py
│   │   │   ├── __eNutsApplications.py
│   │   │   ├── __shell.py
│   │   │   ├── device/
│   │   │   ├── theme/
│   │   │   │   └── __theme.py
│   │   │   └── workspace/
│   │   │       └── __workSpace.py
│   │   ├── apps/
│   │   │   ├── main.py
│   │   │   └── mainX.py
│   │   ├── configuration/
│   │   │   ├── __eNutsConfiguration.py
│   │   │   └── __information.py
│   │   ├── types/
│   │   │   ├── .ff
│   │   │   └── interface/
│   │   │       ├── .ff
│   │   │       ├── UI/
│   │   │       │   └── windows/
│   │   │       │       └── __mainWindow.py
│   │   │       ├── application/
│   │   │       │   ├── __applicationInformation.py
│   │   │       │   └── __shell.py
│   │   │       └── configuration/
│   │   │           └── __eNutsConfiguration.py
│   │   └── utilities/
│   │       └── asyncADB/
│   ├── fluxCore/
│   │   ├── .fff
│   │   ├── action/
│   │   │   ├── __action.py
│   │   │   └── android/
│   │   │       ├── __androidAction.py
│   │   │       ├── __const.py
│   │   │       ├── enums/
│   │   │       │   ├── __eCommands.py
│   │   │       │   ├── __eKeyCode.py
│   │   │       │   ├── __eKeyState.py
│   │   │       │   ├── __eMetaState.py
│   │   │       │   ├── __ePanelCommand.py
│   │   │       │   └── __ePowerMode.py
│   │   │       ├── gesture/
│   │   │       │   ├── __tap.py
│   │   │       │   └── __touch.py
│   │   │       └── injectKey/
│   │   │           ├── __injectKey.py
│   │   │           ├── __injectKeyBase.py
│   │   │           ├── __injectKeyPress.py
│   │   │           └── __injectKeyRelease.py
│   │   ├── device/
│   │   │   └── __device.py
│   │   ├── deviceInput/
│   │   ├── devices/
│   │   │   └── __scrcpy.py
│   │   ├── emitters/
│   │   │   └── scrcpy/
│   │   │       └── __SCRCPYEmitter.py
│   │   ├── types/
│   │   │   ├── .fff
│   │   │   ├── geometry/
│   │   │   │   ├── __circle.py
│   │   │   │   ├── __point.py
│   │   │   │   └── __rectangle.py
│   │   │   ├── interface/
│   │   │   │   ├── action/
│   │   │   │   │   ├── __actionMetadata.py
│   │   │   │   │   └── __androidAction.py
│   │   │   │   ├── device/
│   │   │   │   │   └── __device.py
│   │   │   │   ├── deviceInput/
│   │   │   │   ├── devices/
│   │   │   │   │   └── __scrcpy.py
│   │   │   │   ├── emitters/
│   │   │   │   │   └── __SCRCPYEmitter.py
│   │   │   │   ├── geometry/
│   │   │   │   │   ├── __geoBase.py
│   │   │   │   │   └── __point.py
│   │   │   │   ├── packets/
│   │   │   │   │   ├── __frame.py
│   │   │   │   │   └── __packet.py
│   │   │   │   └── sockets/
│   │   │   │       ├── __controlSocket.py
│   │   │   │       ├── __socket.py
│   │   │   │       └── __videoSocket.py
│   │   │   ├── packets/
│   │   │   │   ├── __frame.py
│   │   │   │   └── __packet.py
│   │   │   └── sockets/
│   │   │       ├── __controlSocket.py
│   │   │       ├── __socket.py
│   │   │       └── __videoSocket.py
│   │   └── utilities/
│   │       ├── __adbutils.py
│   │       ├── __frame.py
│   │       ├── __socket.py
│   │       └── scrcpy/
│   │           ├── __scrcpy.py
│   │           └── __scrcpyConfig.py
│   ├── jAGFx/
│   │   ├── .fff
│   │   ├── IPC/
│   │   │   ├── __IOQueue.py
│   │   │   └── __message.py
│   │   ├── collections/
│   │   │   ├── __tsDictionary.py
│   │   │   └── __tsList.py
│   │   ├── configuration/
│   │   │   ├── __applicationConfig.py
│   │   │   └── __configuration.py
│   │   ├── globals/
│   │   │   └── serializer.py
│   │   ├── logging/
│   │   │   ├── __log.py
│   │   │   ├── __logging.py
│   │   │   ├── __utilities.py
│   │   │   ├── data/
│   │   │   │   ├── __baseSourceInformation.py
│   │   │   │   └── __callerInformation.py
│   │   │   ├── filters/
│   │   │   │   └── __namespaceFilter.py
│   │   │   ├── formatters/
│   │   │   │   └── __defaultFormatter.py
│   │   │   └── handlers/
│   │   │       ├── __dateRotatingFileHandler.py
│   │   │       └── __dynamicQueueHandler.py
│   │   ├── names/
│   │   │   ├── __helpers.py
│   │   │   └── __names.py
│   │   ├── serializer/
│   │   │   ├── __serializable.py
│   │   │   └── __utilities.py
│   │   ├── services/
│   │   │   ├── __asyncProcess.py
│   │   │   ├── __asyncService.py
│   │   │   └── __subscription.py
│   │   ├── singleton/
│   │   │   └── __singleton.py
│   │   ├── types/
│   │   │   ├── __ANSIColors.py
│   │   │   ├── __color.py
│   │   │   ├── __typeChecks.py
│   │   │   └── interface/
│   │   │       ├── .fff
│   │   │       ├── communication/
│   │   │       │   ├── __IOQueue.py
│   │   │       │   └── __message.py
│   │   │       ├── configuration/
│   │   │       │   ├── __applicationConfiguration.py
│   │   │       │   └── __configuration.py
│   │   │       ├── logger/
│   │   │       │   └── __sourceInformation.py
│   │   │       ├── serializer/
│   │   │       │   └── __serializable.py
│   │   │       └── services/
│   │   │           ├── __services.py
│   │   │           └── __subscription.py
│   │   └── workflow/
│   │       └── __workflow.py
│   ├── jAGQt/
│   │   ├── .ff
│   │   ├── animations/
│   │   │   ├── __animationBase.py
│   │   │   ├── __pixmapUtils.py
│   │   │   ├── __sizeAnimationBase.py
│   │   │   ├── blinds/
│   │   │   │   ├── __blindsAnimationBase.py
│   │   │   │   ├── __blindsIn.py
│   │   │   │   ├── __blindsOut.py
│   │   │   │   ├── __blindsTransition.py
│   │   │   │   └── __eBlindsOrientation.py
│   │   │   ├── drawer/
│   │   │   │   ├── __drawerAnimationBase.py
│   │   │   │   ├── __drawerIn.py
│   │   │   │   ├── __drawerOut.py
│   │   │   │   ├── __drawerTransition.py
│   │   │   │   └── __eDrawerDirection.py
│   │   │   ├── rubberband/
│   │   │   │   └── __rubberBand.py
│   │   │   └── wipe/
│   │   │       ├── __eWipeMode.py
│   │   │       ├── __wipeAnimationBase.py
│   │   │       ├── __wipeIn.py
│   │   │       ├── __wipeOut.py
│   │   │       └── __wipeTransition.py
│   │   ├── icons/
│   │   │   └── animations/
│   │   ├── options/
│   │   │   ├── __animationOptions.py
│   │   │   ├── __optionsBase.py
│   │   │   └── __sideBarOptions.py
│   │   ├── types/
│   │   │   ├── .fff
│   │   │   └── interface/
│   │   │       ├── .fff
│   │   │       ├── animations/
│   │   │       │   └── __animation.py
│   │   │       ├── components/
│   │   │       │   └── __componentBase.py
│   │   │       ├── icons/
│   │   │       │   └── animation/
│   │   │       ├── qt/
│   │   │       │   └── __qwindow.py
│   │   │       ├── widgets/
│   │   │       │   ├── __page.py
│   │   │       │   ├── commandBar/
│   │   │       │   │   ├── __commandBar.py
│   │   │       │   │   ├── __commandBarButton.py
│   │   │       │   │   └── __commandBarGroup.py
│   │   │       │   ├── dashboard/
│   │   │       │   └── icons/
│   │   │       └── window/
│   │   │           ├── __mainWindowBase.py
│   │   │           └── windowBase/
│   │   │               └── __windowBase.py
│   │   ├── utilities/
│   │   │   ├── __animation.py
│   │   │   ├── __layout.py
│   │   │   └── __pushButton.py
│   │   ├── widgets/
│   │   │   ├── components/
│   │   │   │   ├── __componentBase.py
│   │   │   │   └── __objectName.py
│   │   │   ├── dashboard/
│   │   │   ├── header/
│   │   │   ├── icon/
│   │   │   │   ├── __icon.py
│   │   │   │   └── __stateFullIcon.py
│   │   │   ├── image/
│   │   │   │   └── __image.py
│   │   │   ├── page/
│   │   │   ├── sideBar/
│   │   │   │   ├── __eSideBarState.py
│   │   │   │   ├── __sideBar.py
│   │   │   │   ├── components/
│   │   │   │   │   ├── __sideBarHeader.py
│   │   │   │   │   └── __sideBarItem.py
│   │   │   │   └── menu/
│   │   │   │       ├── __eSideBarMenuRole.py
│   │   │   │       ├── __sideBarMenu.py
│   │   │   │       └── __sideBarMenuItem.py
│   │   │   └── text/
│   │   │       ├── __description.py
│   │   │       ├── __text.py
│   │   │       └── __title.py
│   │   └── window/
│   │       ├── __mainWindowBase.py
│   │       └── windowBase/
│   │           └── __windowBase.py
│   ├── main.py
│   └── utilities/
│       ├── __asyncio.py
│       ├── __cacheClean.py
│       ├── __frame.py
│       ├── __helpers.py
│       ├── __module.py
│       ├── __sysArguments.py
│       └── io/
│           └── __io.py
├── typings/
│   └── __builtins__.pyi
└── update_inventory.yml
```

---

## File Details & Code Components

```text
.scripts:
	updateInventory.py - 
		FUNCTION(S):
			_runGitCommand -> : _rungitcommand
			_shouldIncludeFile -> : _shouldincludefile
			_findDocPath -> : _finddocpath
			_parsePythonFile -> : _parsepythonfile
			_parseChangeHistory -> : _parsechangehistory
			_buildTreeLines -> : _buildtreelines
			_buildFileDetailsLines -> : _buildfiledetailslines
			generateInventory -> : generateinventory
		CONSTANTS(S)/GLOBAL(S)
			C_TARGET_DIR -> : c_target_dir
			C_DOCS_DIR -> : c_docs_dir
			C_OUTPUT_FILE -> : c_output_file
			C_MAX_COMMITS -> : c_max_commits
			C_EXCLUDED_EXTENSIONS -> : c_excluded_extensions
			C_EXCLUDED_DIRECTORIES -> : c_excluded_directories
			C_EXCLUDED_FILES -> : c_excluded_files
			C_EXCLUDED_VARIABLES -> : c_excluded_variables

src:
	__monkeyPatch.py - 
	main.py - 
		FUNCTION(S):
			_program -> : _program
			program -> : program
		CONSTANTS(S)/GLOBAL(S)
			LOG_LEVEL -> : log_level
			THIRD_PARTY_LOG_LEVEL -> : third_party_log_level
			THIRD_PARTY_LOGGERS -> : third_party_loggers

src/eNuts/application:
	__applicationInformation.py - 
		CLASSE(S):
			ApplicationInformation -> : applicationinformation
	__eNutsApplications.py - 
		CLASSE(S):
			eNutsApplication -> : enutsapplication
		CONSTANTS(S)/GLOBAL(S)
			CONFIG_DIR -> : config_dir
	__shell.py - 
		CLASSE(S):
			Shell -> : shell

src/eNuts/application/theme:
	__theme.py - 
		FUNCTION(S):
			loadStyles -> : loadstyles
			_loadPalette -> : _loadpalette
			loadStyle -> : loadstyle

src/eNuts/application/workspace:
	__workSpace.py - 
		CLASSE(S):
			WorkSpace -> : workspace
		CONSTANTS(S)/GLOBAL(S)
			C_SIDEBAR_ANIMATION_TYPE -> : c_sidebar_animation_type
			C_SIDEBAR_ANIMATION_MS -> : c_sidebar_animation_ms
			QSPolicy -> : qspolicy
			StyleBackground -> : stylebackground

src/eNuts/apps:
	main.py - 
		FUNCTION(S):
			main -> : main
			program -> : program
	mainX.py - 
		FUNCTION(S):
			main -> : main
			program -> : program

src/eNuts/configuration:
	__eNutsConfiguration.py - 
		CLASSE(S):
			eNutsConfiguration -> : enutsconfiguration
		CONSTANTS(S)/GLOBAL(S)
			CONFIG_PATH -> : config_path
	__information.py - 
		CLASSE(S):
			ApplicationInformation -> : applicationinformation

src/eNuts/types/interface/application:
	__applicationInformation.py - 
		CLASSE(S):
			iApplicationInformation -> : iapplicationinformation
	__shell.py - 
		CLASSE(S):
			iShell -> : ishell

src/eNuts/types/interface/configuration:
	__eNutsConfiguration.py - 
		CLASSE(S):
			iENUTSConfiguration -> : ienutsconfiguration

src/eNuts/types/interface/UI/windows:
	__mainWindow.py - 
		CLASSE(S):
			iENUTSWindow -> : ienutswindow

src/eNuts/UI/navigation:
	__sideBarMenuBuilder.py - 
		FUNCTION(S):
			_onMenuItemClicked -> : _onmenuitemclicked
			buildSmokeTestSideBarMenu -> : buildsmoketestsidebarmenu

src/eNuts/UI/widgets/pages/recorder:
	__recorderPage.py - 
		CLASSE(S):
			KAndGRecorderPage -> : kandgrecorderpage

src/eNuts/UI/widgets/pages/settings:
	__settingsPage.py - 
		CLASSE(S):
			SettingsPage -> : settingspage
		FUNCTION(S):
			_applyThemePalette -> : _applythemepalette
		CONSTANTS(S)/GLOBAL(S)
			C_THEME_NAMES -> : c_theme_names
			C_DARK_THEMES -> : c_dark_themes

src/eNuts/UI/widgets/spinners:
	__evolvingNeuralBrain.py - 
		CLASSE(S):
			_BrainBakeWorker -> : _brainbakeworker
			EvolvingNeuralBrain -> : evolvingneuralbrain
		FUNCTION(S):
			_hash01 -> : _hash01
			_brainPoint -> : _brainpoint
	__evolvingNeuralOrb.py - 
		CLASSE(S):
			_MeshBakeWorker -> : _meshbakeworker
			EvolvingNeuralOrb -> : evolvingneuralorb
		FUNCTION(S):
			_spherePoint -> : _spherepoint
	__revolvingNeuralOrb.py - 
		CLASSE(S):
			RevolvingNeuralOrb -> : revolvingneuralorb

src/eNuts/UI/windows:
	__mainWindow.py - 
		CLASSE(S):
			ENUTSWindow -> : enutswindow

src/fluxCore/action:
	__action.py - 
		CLASSE(S):
			Action -> : action
		CONSTANTS(S)/GLOBAL(S)
			DEVICE_MINIMUM_WAIT -> : device_minimum_wait

src/fluxCore/action/android:
	__androidAction.py - 
		CLASSE(S):
			AndroidAction -> : androidaction
	__const.py - 
		CONSTANTS(S)/GLOBAL(S)
			PRESSURE_MAX -> : pressure_max
			PRESSURE_MIN -> : pressure_min
			PRIMARY_BUTTON -> : primary_button
			DEFAULT_FINGER_ID -> : default_finger_id

src/fluxCore/action/android/enums:
	__eCommands.py - 
		CLASSE(S):
			eCommandType -> : ecommandtype
	__eKeyCode.py - 
		CLASSE(S):
			eKeyCode -> : ekeycode
	__eKeyState.py - 
		CLASSE(S):
			eKeyState -> : ekeystate
	__eMetaState.py - 
		CLASSE(S):
			eMetaState -> : emetastate
	__ePanelCommand.py - 
		CLASSE(S):
			ePanelCommand -> : epanelcommand
	__ePowerMode.py - 
		CLASSE(S):
			ePowerMode -> : epowermode

src/fluxCore/action/android/gesture:
	__tap.py - 
		CLASSE(S):
			Tap -> : tap
	__touch.py - 
		CLASSE(S):
			Touch -> : touch

src/fluxCore/action/android/injectKey:
	__injectKey.py - 
		CLASSE(S):
			InjectKey -> : injectkey
	__injectKeyBase.py - 
		CLASSE(S):
			InjectKeyBase -> : injectkeybase
	__injectKeyPress.py - 
		CLASSE(S):
			InjectKeyPress -> : injectkeypress
	__injectKeyRelease.py - 
		CLASSE(S):
			InjectKeyRelease -> : injectkeyrelease

src/fluxCore/device:
	__device.py - 
		CLASSE(S):
			Device -> : device

src/fluxCore/devices:
	__scrcpy.py - 
		CLASSE(S):
			SCRCPY -> : scrcpy

src/fluxCore/emitters/scrcpy:
	__SCRCPYEmitter.py - 
		CLASSE(S):
			SCRCPYEmitter -> : scrcpyemitter
		CONSTANTS(S)/GLOBAL(S)
			JAR_NAME -> : jar_name
			SERVER_PATH -> : server_path
			ANDROID_PATH -> : android_path
			MAX_SIZE -> : max_size
			MAX_FPS -> : max_fps
			BITRATE -> : bitrate

src/fluxCore/types/geometry:
	__circle.py - 
		CLASSE(S):
			Circle -> : circle
	__point.py - 
		CLASSE(S):
			Point -> : point
	__rectangle.py - 
		CLASSE(S):
			Rectangle -> : rectangle

src/fluxCore/types/interface/action:
	__actionMetadata.py - 
		CLASSE(S):
			iActionMetadata -> : iactionmetadata
		CONSTANTS(S)/GLOBAL(S)
			DEVICE_MINIMUM_WAIT -> : device_minimum_wait
	__androidAction.py - 
		CLASSE(S):
			iAndroidAction -> : iandroidaction

src/fluxCore/types/interface/device:
	__device.py - 
		CLASSE(S):
			iDevice -> : idevice

src/fluxCore/types/interface/devices:
	__scrcpy.py - 
		CLASSE(S):
			iSCRCPY -> : iscrcpy

src/fluxCore/types/interface/emitters:
	__SCRCPYEmitter.py - 
		CLASSE(S):
			iSCRCPYEmitter -> : iscrcpyemitter

src/fluxCore/types/interface/geometry:
	__geoBase.py - 
		CLASSE(S):
			iGeometry -> : igeometry
	__point.py - 
		CLASSE(S):
			iPoint -> : ipoint

src/fluxCore/types/interface/packets:
	__frame.py - 
		CLASSE(S):
			iFrame -> : iframe
	__packet.py - 
		CLASSE(S):
			iPacket -> : ipacket

src/fluxCore/types/interface/sockets:
	__controlSocket.py - 
		CLASSE(S):
			iControlSocket -> : icontrolsocket
	__socket.py - 
		CLASSE(S):
			iSocket -> : isocket
	__videoSocket.py - 
		CLASSE(S):
			iVideoSocket -> : ivideosocket

src/fluxCore/types/packets:
	__frame.py - 
		CLASSE(S):
			Frame -> : frame
	__packet.py - 
		CLASSE(S):
			Packet -> : packet

src/fluxCore/types/sockets:
	__controlSocket.py - 
		CLASSE(S):
			ControlSocket -> : controlsocket
	__socket.py - 
		CLASSE(S):
			SocketBase -> : socketbase
	__videoSocket.py - 
		CLASSE(S):
			VideoSocket -> : videosocket

src/fluxCore/utilities:
	__adbutils.py - 
		FUNCTION(S):
			getADBDevice -> : getadbdevice
	__frame.py - 
		FUNCTION(S):
			_ParseFrameHeader -> : _parseframeheader
			ReadSingleFrame -> : readsingleframe
			AsyncReadSingleFrame -> : asyncreadsingleframe
		CONSTANTS(S)/GLOBAL(S)
			C_MAX_FRAME_BYTES -> : c_max_frame_bytes
			C_FLAG_CONFIG -> : c_flag_config
			C_FLAG_KEYFRAME -> : c_flag_keyframe
			C_PTS_MASK -> : c_pts_mask
	__socket.py - 
		FUNCTION(S):
			ReadExact -> : readexact
			AsyncReadExact -> : asyncreadexact
			ReadAll -> : readall
			AsyncReadAll -> : asyncreadall
		CONSTANTS(S)/GLOBAL(S)
			C_RECV_CHUNK -> : c_recv_chunk

src/fluxCore/utilities/scrcpy:
	__scrcpy.py - 
		FUNCTION(S):
			isSCRCPYServerDeployed -> : isscrcpyserverdeployed
			pushSCRCPYServer -> : pushscrcpyserver
			deployServer -> : deployserver
			getSCRCPYADBSocket -> : getscrcpyadbsocket
			createCodecContext -> : createcodeccontext
		CONSTANTS(S)/GLOBAL(S)
			JAR_NAME -> : jar_name
			SERVER_PATH -> : server_path
			ANDROID_PATH -> : android_path
			MAX_SIZE -> : max_size
			MAX_FPS -> : max_fps
			BITRATE -> : bitrate
	__scrcpyConfig.py - 
		CLASSE(S):
			SCRCPYServerConfig -> : scrcpyserverconfig

src/jAGFx/collections:
	__tsDictionary.py - 
		CLASSE(S):
			TSDictionary -> : tsdictionary
	__tsList.py - 
		CLASSE(S):
			TSList -> : tslist

src/jAGFx/configuration:
	__applicationConfig.py - 
		CLASSE(S):
			ApplicationConfiguration -> : applicationconfiguration
		CONSTANTS(S)/GLOBAL(S)
			CONFIG_PATH -> : config_path
			CONFIG_FILENAME -> : config_filename
	__configuration.py - 
		CLASSE(S):
			Configuration -> : configuration

src/jAGFx/globals:
	serializer.py - 
		CONSTANTS(S)/GLOBAL(S)
			KNOWN_TYPES -> : known_types

src/jAGFx/IPC:
	__IOQueue.py - 
		CLASSE(S):
			IOQueue -> : ioqueue
	__message.py - 
		CLASSE(S):
			Message -> : message

src/jAGFx/logging:
	__log.py - 
	__logging.py - 
		FUNCTION(S):
			_resolveErr -> : _resolveerr
			verbose -> : verbose
			debug -> : debug
			info -> : info
			warning -> : warning
			error -> : error
			critical -> : critical
			fatal -> : fatal
			_exitOnError -> : _exitonerror
		CONSTANTS(S)/GLOBAL(S)
			VERBOSE -> : verbose
			EXITONERROR -> : exitonerror
	__utilities.py - 
		FUNCTION(S):
			_getConsoleLogger -> : _getconsolelogger
			_refreshQueueListener -> : _refreshqueuelistener
			setupLogging -> : setuplogging
			addFileHandler -> : addfilehandler
			removeFileHandler -> : removefilehandler
			setNamespaceLevel -> : setnamespacelevel
			suppressedLogger -> : suppressedlogger
			unsuppressedLogger -> : unsuppressedlogger
			stopLogging -> : stoplogging
		CONSTANTS(S)/GLOBAL(S)
			DEF_FILE_HANDLER -> : def_file_handler
			DEF_FILE_FORMATTER -> : def_file_formatter
			C_LOG_FORMAT -> : c_log_format
			C_LOG_COLORS -> : c_log_colors
			C_SECONDARY_COLORS -> : c_secondary_colors
			G_LOG_QUEUE -> : g_log_queue
			G_LOG_LISTENER -> : g_log_listener
			G_ACTIVE_HANDLERS -> : g_active_handlers
			G_NAMESPACE_LEVELS -> : g_namespace_levels
			G_DEFAULT_LEVEL -> : g_default_level
			EXITONERROR -> : exitonerror
			fmtList -> : fmtlist

src/jAGFx/logging/data:
	__baseSourceInformation.py - 
		CLASSE(S):
			BaseSourceInformation -> : basesourceinformation
	__callerInformation.py - 
		CLASSE(S):
			CallerInformation -> : callerinformation

src/jAGFx/logging/filters:
	__namespaceFilter.py - 
		CLASSE(S):
			NamespaceFilter -> : namespacefilter

src/jAGFx/logging/formatters:
	__defaultFormatter.py - 
		CLASSE(S):
			DefaultFormatter -> : defaultformatter
		CONSTANTS(S)/GLOBAL(S)
			C_LOG_FORMAT -> : c_log_format
			C_LOG_COLORS -> : c_log_colors
			C_SECONDARY_COLORS -> : c_secondary_colors
			fmtList -> : fmtlist

src/jAGFx/logging/handlers:
	__dateRotatingFileHandler.py - 
		CLASSE(S):
			DateRotatingFileHandler -> : daterotatingfilehandler
	__dynamicQueueHandler.py - 
		CLASSE(S):
			DynamicQueueHandler -> : dynamicqueuehandler

src/jAGFx/names:
	__helpers.py - 
		FUNCTION(S):
			getRandomName -> : getrandomname
			resetNames -> : resetnames
			name -> : name
	__names.py - 
		CLASSE(S):
			_names -> : _names

src/jAGFx/serializer:
	__serializable.py - 
		CLASSE(S):
			Serializable -> : serializable
	__utilities.py - 
		FUNCTION(S):
			_decodeEnum -> : _decodeenum
			_decodeSerializeable -> : _decodeserializeable
			_decodeFunction -> : _decodefunction
			_decodeCustomType -> : _decodecustomtype
			jsonDecode -> : jsondecode
			importClass -> : importclass

src/jAGFx/services:
	__asyncProcess.py - 
		CLASSE(S):
			AsyncProcess -> : asyncprocess
	__asyncService.py - 
		CLASSE(S):
			AsyncService -> : asyncservice
	__subscription.py - 
		CLASSE(S):
			Subscription -> : subscription
			AsyncSubscription -> : asyncsubscription

src/jAGFx/singleton:
	__singleton.py - 
		CLASSE(S):
			SingletonM -> : singletonm
		FUNCTION(S):
			SingletonF -> : singletonf
			SingletonC -> : singletonc
		CONSTANTS(S)/GLOBAL(S)
			_SINGLETONINSTANCES -> : _singletoninstances
			_INSTANCELOCK -> : _instancelock

src/jAGFx/types:
	__ANSIColors.py - 
		CLASSE(S):
			eAnsiColors -> : eansicolors
	__color.py - 
		CLASSE(S):
			Color -> : color
	__typeChecks.py - 
		FUNCTION(S):
			isNoOpMethod -> : isnoopmethod
			isUnion -> : isunion
			isAny -> : isany
			isNone -> : isnone
			isListOfT -> : islistoft
			_isStandardType -> : _isstandardtype
			_isGenericType -> : _isgenerictype
			Is -> : is

src/jAGFx/types/interface/communication:
	__IOQueue.py - 
		CLASSE(S):
			iIOQueue -> : iioqueue
	__message.py - 
		CLASSE(S):
			iMessage -> : imessage

src/jAGFx/types/interface/configuration:
	__applicationConfiguration.py - 
		CLASSE(S):
			iApplicationConfiguration -> : iapplicationconfiguration
	__configuration.py - 
		CLASSE(S):
			iConfiguration -> : iconfiguration

src/jAGFx/types/interface/logger:
	__sourceInformation.py - 
		CLASSE(S):
			iSourceInformation -> : isourceinformation

src/jAGFx/types/interface/serializer:
	__serializable.py - 
		CLASSE(S):
			iSerializable -> : iserializable

src/jAGFx/types/interface/services:
	__services.py - 
		CLASSE(S):
			iService -> : iservice
	__subscription.py - 
		CLASSE(S):
			iSubscription -> : isubscription

src/jAGFx/workflow:
	__workflow.py - 
		FUNCTION(S):
			_normalize_workflow_name -> : _normalize_workflow_name
			_discover_workflows -> : _discover_workflows
			_run_workflow -> : _run_workflow
			_wrap_init -> : _wrap_init
			_prepare_subclass -> : _prepare_subclass
			_install_subclass_hook -> : _install_subclass_hook
			workflow -> : workflow
			workflow -> : workflow
			workflow -> : workflow
		CONSTANTS(S)/GLOBAL(S)
			_T -> : _t
			_SYNC_WF_PREFIX -> : _sync_wf_prefix
			_ASYNC_WF_PREFIX -> : _async_wf_prefix
			_WORKFLOW_METADATA -> : _workflow_metadata
			_WORKFLOW_ASYNC -> : _workflow_async
			_WORKFLOW_GUARD -> : _workflow_guard
			_WORKFLOW_INIT_WRAPPED -> : _workflow_init_wrapped
			_WORKFLOW_SUBCLASS_WRAPPED -> : _workflow_subclass_wrapped

src/jAGQt/animations:
	__animationBase.py - 
		CLASSE(S):
			AnimationBase -> : animationbase
		CONSTANTS(S)/GLOBAL(S)
			C_DEFAULT_DURATION_MS -> : c_default_duration_ms
	__pixmapUtils.py - 
		FUNCTION(S):
			assertSetPixmap -> : assertsetpixmap
			toPixmap -> : topixmap
			grabWidget -> : grabwidget
			scaleToTarget -> : scaletotarget
			applyPixmap -> : applypixmap
		CONSTANTS(S)/GLOBAL(S)
			ImageLike -> : imagelike
	__sizeAnimationBase.py - 
		CLASSE(S):
			SizeAnimationBase -> : sizeanimationbase

src/jAGQt/animations/blinds:
	__blindsAnimationBase.py - 
		CLASSE(S):
			BlindsAnimationBase -> : blindsanimationbase
		CONSTANTS(S)/GLOBAL(S)
			C_DEFAULT_STRIPS -> : c_default_strips
	__blindsIn.py - 
		CLASSE(S):
			BlindsIn -> : blindsin
	__blindsOut.py - 
		CLASSE(S):
			BlindsOut -> : blindsout
	__blindsTransition.py - 
		CLASSE(S):
			BlindsTransition -> : blindstransition
	__eBlindsOrientation.py - 
		CLASSE(S):
			eBlindsOrientation -> : eblindsorientation

src/jAGQt/animations/drawer:
	__drawerAnimationBase.py - 
		CLASSE(S):
			DrawerAnimationBase -> : draweranimationbase
	__drawerIn.py - 
		CLASSE(S):
			DrawerIn -> : drawerin
	__drawerOut.py - 
		CLASSE(S):
			DrawerOut -> : drawerout
	__drawerTransition.py - 
		CLASSE(S):
			DrawerTransition -> : drawertransition
	__eDrawerDirection.py - 
		CLASSE(S):
			eDrawerDirection -> : edrawerdirection

src/jAGQt/animations/rubberband:
	__rubberBand.py - 
		CLASSE(S):
			RubberBand -> : rubberband
		FUNCTION(S):
			_elastic01 -> : _elastic01

src/jAGQt/animations/wipe:
	__eWipeMode.py - 
		CLASSE(S):
			eWipeMode -> : ewipemode
	__wipeAnimationBase.py - 
		CLASSE(S):
			WipeAnimationBase -> : wipeanimationbase
		FUNCTION(S):
			_assertSetPixmap -> : _assertsetpixmap
			_toPixmap -> : _topixmap
		CONSTANTS(S)/GLOBAL(S)
			C_BLADE_WIDTH -> : c_blade_width
			C_BLADE_COLOR -> : c_blade_color
			ImageLike -> : imagelike
	__wipeIn.py - 
		CLASSE(S):
			WipeIn -> : wipein
	__wipeOut.py - 
		CLASSE(S):
			WipeOut -> : wipeout
	__wipeTransition.py - 
		CLASSE(S):
			WipeTransition -> : wipetransition

src/jAGQt/options:
	__animationOptions.py - 
		CLASSE(S):
			AnimationOptions -> : animationoptions
		CONSTANTS(S)/GLOBAL(S)
			C_DEFAULT_DURATION_MS -> : c_default_duration_ms
			C_DEFAULT_NAME -> : c_default_name
	__optionsBase.py - 
		CLASSE(S):
			OptionsBase -> : optionsbase
		CONSTANTS(S)/GLOBAL(S)
			C_OPTIONS_SUBDIR -> : c_options_subdir
			C_THEMES_SUBDIR -> : c_themes_subdir
	__sideBarOptions.py - 
		CLASSE(S):
			SideBarOptions -> : sidebaroptions
		CONSTANTS(S)/GLOBAL(S)
			C_DEFAULT_EXPANDED_WIDTH -> : c_default_expanded_width
			C_DEFAULT_COLLAPSED_WIDTH -> : c_default_collapsed_width
			C_DEFAULT_NAME -> : c_default_name
			C_DEFAULT_MENU_ICON_SIZE -> : c_default_menu_icon_size
			C_DEFAULT_MENU_HEADER_MARGIN -> : c_default_menu_header_margin
			C_DEFAULT_MENU_LEAF_MARGIN -> : c_default_menu_leaf_margin

src/jAGQt/types/interface/animations:
	__animation.py - 
		CLASSE(S):
			iAnimation -> : ianimation

src/jAGQt/types/interface/components:
	__componentBase.py - 
		CLASSE(S):
			iComponentBase -> : icomponentbase

src/jAGQt/types/interface/qt:
	__qwindow.py - 
		CLASSE(S):
			iQMainWindow -> : iqmainwindow

src/jAGQt/types/interface/widgets:
	__page.py - 
		CLASSE(S):
			Page -> : page
		CONSTANTS(S)/GLOBAL(S)
			Policy -> : policy

src/jAGQt/types/interface/widgets/commandBar:
	__commandBar.py - 
		CLASSE(S):
			iCommandBar -> : icommandbar
	__commandBarButton.py - 
		CLASSE(S):
			iCommandBarButton -> : icommandbarbutton
	__commandBarGroup.py - 
		CLASSE(S):
			iCommandBarGroup -> : icommandbargroup

src/jAGQt/types/interface/window:
	__mainWindowBase.py - 
		CLASSE(S):
			iMainWindowBase -> : imainwindowbase

src/jAGQt/types/interface/window/windowBase:
	__windowBase.py - 
		CLASSE(S):
			iWindowBase -> : iwindowbase

src/jAGQt/utilities:
	__animation.py - 
		CLASSE(S):
			AnimationError -> : animationerror
		FUNCTION(S):
			ValidateAnimationTarget -> : validateanimationtarget
			ValidateAnimationRange -> : validateanimationrange
			CreatePropertyAnimation -> : createpropertyanimation
			AnimateProperty -> : animateproperty
	__layout.py - 
		FUNCTION(S):
			newLayout -> : newlayout
			newLayout -> : newlayout
			newLayout -> : newlayout
			contentMargins -> : contentmargins
			_findLayoutParent -> : _findlayoutparent
			_replaceNestedLayout -> : _replacenestedlayout
			replaceLayout -> : replacelayout
	__pushButton.py - 
		CLASSE(S):
			_pushButton -> : _pushbutton
		FUNCTION(S):
			createButton -> : createbutton

src/jAGQt/widgets/components:
	__componentBase.py - 
		CLASSE(S):
			ComponentBase -> : componentbase
	__objectName.py - 
		CLASSE(S):
			ObjectName -> : objectname
		CONSTANTS(S)/GLOBAL(S)
			QSPolicy -> : qspolicy
			StyleBackground -> : stylebackground

src/jAGQt/widgets/icon:
	__icon.py - 
		CLASSE(S):
			Icon -> : icon
	__stateFullIcon.py - 
		CLASSE(S):
			StatefullIcon -> : statefullicon
		CONSTANTS(S)/GLOBAL(S)
			C_DEFAULT_WIPE_MS -> : c_default_wipe_ms

src/jAGQt/widgets/image:
	__image.py - 
		CLASSE(S):
			Image -> : image
			_GLView -> : _glview
		CONSTANTS(S)/GLOBAL(S)
			Backend -> : backend

src/jAGQt/widgets/sideBar:
	__eSideBarState.py - 
		CLASSE(S):
			eSideBarState -> : esidebarstate
	__sideBar.py - 
		CLASSE(S):
			SideBar -> : sidebar
		CONSTANTS(S)/GLOBAL(S)
			C_EXPANDED_WIDTH -> : c_expanded_width
			C_COLLAPSED_WIDTH -> : c_collapsed_width
			C_STATE_ANIM_MS -> : c_state_anim_ms
			QSPolicy -> : qspolicy

src/jAGQt/widgets/sideBar/components:
	__sideBarHeader.py - 
		CLASSE(S):
			SideBarHeader -> : sidebarheader
		CONSTANTS(S)/GLOBAL(S)
			C_ICON_SIZE -> : c_icon_size
			QSPolicy -> : qspolicy
	__sideBarItem.py - 
		CLASSE(S):
			SideBarItem -> : sidebaritem
		CONSTANTS(S)/GLOBAL(S)
			QSPolicy -> : qspolicy
			StyleBackground -> : stylebackground

src/jAGQt/widgets/sideBar/menu:
	__eSideBarMenuRole.py - 
		CLASSE(S):
			eSideBarMenuRole -> : esidebarmenurole
	__sideBarMenu.py - 
		CLASSE(S):
			SideBarMenu -> : sidebarmenu
		CONSTANTS(S)/GLOBAL(S)
			QSPolicy -> : qspolicy
			StyleBackground -> : stylebackground
	__sideBarMenuItem.py - 
		CLASSE(S):
			SideBarMenuItem -> : sidebarmenuitem
		FUNCTION(S):
			_defaultIconPath -> : _defaulticonpath
		CONSTANTS(S)/GLOBAL(S)
			C_ICON_SIZE -> : c_icon_size
			C_HEADER_MARGIN -> : c_header_margin
			C_LEAF_MARGIN -> : c_leaf_margin
			C_DEFAULT_ICON -> : c_default_icon
			QSPolicy -> : qspolicy

src/jAGQt/widgets/text:
	__description.py - 
		CLASSE(S):
			Description -> : description
		CONSTANTS(S)/GLOBAL(S)
			QPolicy -> : qpolicy
	__text.py - 
		CLASSE(S):
			Text -> : text
		CONSTANTS(S)/GLOBAL(S)
			EMode -> : emode
			QPolicy -> : qpolicy
	__title.py - 
		CLASSE(S):
			Title -> : title
		CONSTANTS(S)/GLOBAL(S)
			QPolicy -> : qpolicy

src/jAGQt/window:
	__mainWindowBase.py - 
		CLASSE(S):
			MainWindowBase -> : mainwindowbase

src/jAGQt/window/windowBase:
	__windowBase.py - 
		CLASSE(S):
			WindowBase -> : windowbase

src/utilities:
	__asyncio.py - 
		FUNCTION(S):
			getRunningLoop -> : getrunningloop
			getEventLoop -> : geteventloop
			createTask -> : createtask
	__cacheClean.py - 
		FUNCTION(S):
			PyCacheClean -> : pycacheclean
		CONSTANTS(S)/GLOBAL(S)
			CLEARNER_TARGET -> : clearner_target
	__frame.py - 
		FUNCTION(S):
			getCallersFrame -> : getcallersframe
			FormatFrame -> : formatframe
			getFrameInfo -> : getframeinfo
			getCallableFromFrame -> : getcallablefromframe
			formatTrace -> : formattrace
		CONSTANTS(S)/GLOBAL(S)
			IGNORE_MODULES -> : ignore_modules
	__helpers.py - 
		FUNCTION(S):
			StripAnsi -> : stripansi
		CONSTANTS(S)/GLOBAL(S)
			ANSI_RE -> : ansi_re
	__module.py - 
		CLASSE(S):
			launchModule -> : launchmodule
	__sysArguments.py - 
		FUNCTION(S):
			RebuildArguments -> : rebuildarguments
			ProcessArguments -> : processarguments

src/utilities/io:
	__io.py - 
		FUNCTION(S):
			getAssetPath -> : getassetpath
			getStylePath -> : getstylepath
			getFontPath -> : getfontpath
			getICONPath -> : geticonpath
			getConfigPath -> : getconfigpath
			getStyleSheet -> : getstylesheet
			LoadCFG -> : loadcfg
			SaveCFG -> : savecfg
		CONSTANTS(S)/GLOBAL(S)
			ASSETSDIR -> : assetsdir
			CONFIGDIR -> : configdir
			FONTDIR -> : fontdir
			STYLEDIR -> : styledir
			ICONDIR -> : icondir

```

---

## Change Summary

```text
2a884a9:
	Merge branch 'development' of https://github.com/IAmJAG/eNuts into development

9263ffe:
	fix(SideBar): shorten "Key & Gesture Recorder" to "K&G Recorder"
		src/eNuts/UI/navigation/__sideBarMenuBuilder.py

b1ce6a2:
	feat(SideBar): store/push menu metrics from SideBarOptions to menu and footer
		src/jAGQt/widgets/SideBar/__sideBar.py

6a74e25:
	feat(SideBar): apply menu metrics from options to menu items
		src/jAGQt/widgets/SideBar/menu/__sideBarMenu.py
		src/jAGQt/widgets/SideBar/menu/__sideBarMenuItem.py

28f636d:
	feat(SideBarOptions): menu header/leaf size metrics applied in code
		src/jAGQt/options/__sideBarOptions.py

db1613f:
	fix(SideBar): leaf indent in code, default logo icon, Settings as footer
		src/eNuts/UI/navigation/__sideBarMenuBuilder.py
		src/eNuts/application/workspace/__workSpace.py
		src/jAGQt/widgets/SideBar/__sideBar.py
		src/jAGQt/widgets/SideBar/menu/__sideBarMenuItem.py

c8309b3:
	fix(theme): indent SideBar leaf items with margin-left (padding ignored by layout)
		config/themes/dark/main.css

8665bb3:
	debug(theme): loud SideBar menu backgrounds to verify QSS role selectors
		config/themes/dark/main.css

f5482bb:
	Merge branch 'development' of https://github.com/IAmJAG/eNuts into development

2d63fd0:
	fix: correct import case for SideBar module
		src/eNuts/UI/navigation/__sideBarMenuBuilder.py

```