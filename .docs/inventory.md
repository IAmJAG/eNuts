# eNuts Asset & Directory Inventory
*Auto-generated on: 2026-10-14 08:09:57 UTC*

## Current Directory Structure

```text
eNuts/
├── .bin/
│   └── scrcpy-server.jar
├── .gitignore
├── .kilocode/
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
│   └── eNuts/
│       └── appconfig.json
├── src/
│   ├── __monkeyPatch.py
│   ├── eNuts/
│   │   ├── .ff
│   │   ├── UI/
│   │   │   ├── .ff
│   │   │   ├── widgets/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── recorder/
│   │   │   │   │   │   └── __recorderPage.py
│   │   │   │   │   └── settings/
│   │   │   │   │       └── __settingsPage.py
│   │   │   │   └── spinners/
│   │   │   │       ├── __evolvingNeuralBrain.py
│   │   │   │       ├── __evolvingNeuralOrb.py
│   │   │   │       └── __revolvingNeuralOrb.py
│   │   │   └── windows/
│   │   │       └── __mainWindow.py
│   │   ├── application/
│   │   │   ├── __eNutsApplication.py
│   │   │   ├── __eNutsService.py
│   │   │   ├── __shell.py
│   │   │   └── theme/
│   │   │       └── __theme.py
│   │   ├── apps/
│   │   │   ├── main.py
│   │   │   └── training.py
│   │   ├── configuration/
│   │   │   ├── __eNutsConfiguration.py
│   │   │   └── __information.py
│   │   └── types/
│   │       ├── .ff
│   │       └── interface/
│   │           ├── .ff
│   │           ├── application/
│   │           │   ├── __enutsService.py
│   │           │   └── __shell.py
│   │           └── configuration/
│   │               └── __eNutsConfiguration.py
│   ├── fluxCore/
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
│   │   ├── devices/
│   │   │   └── __scrcpy.py
│   │   ├── emitters/
│   │   │   └── scrcpy/
│   │   │       └── __SCRCPYEmitter.py
│   │   ├── types/
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
│   │   ├── types/
│   │   │   └── interface/
│   │   │       ├── components/
│   │   │       │   └── __componentBase.py
│   │   │       ├── widgets/
│   │   │       │   ├── __page.py
│   │   │       │   └── commandBar/
│   │   │       │       ├── __commandBar.py
│   │   │       │       ├── __commandBarButton.py
│   │   │       │       └── __commandBarGroup.py
│   │   │       └── window/
│   │   │           ├── __mainWindowBase.py
│   │   │           └── windowBase/
│   │   │               └── __windowBase.py
│   │   ├── utilities/
│   │   │   ├── __animation.py
│   │   │   ├── __layout.py
│   │   │   └── __pushButton.py
│   │   ├── widgets/
│   │   │   ├── Image/
│   │   │   │   └── __image.py
│   │   │   ├── SideBar/
│   │   │   │   ├── __sideBar.py
│   │   │   │   └── components/
│   │   │   │       ├── __sideBarContent.py
│   │   │   │       ├── __sideBarGroup.py
│   │   │   │       ├── __sideBarHeader.py
│   │   │   │       ├── __sideBarIcon.py
│   │   │   │       ├── __sideBarItem.py
│   │   │   │       ├── __sideBarSeparator.py
│   │   │   │       └── __sideBarText.py
│   │   │   ├── __header.py
│   │   │   ├── commandBar/
│   │   │   │   ├── __base.py
│   │   │   │   ├── __commandBar.py
│   │   │   │   ├── __commandBarGroup.py
│   │   │   │   └── commandBarButton/
│   │   │   │       ├── __base.py
│   │   │   │       └── __commandBarButton.py
│   │   │   ├── components/
│   │   │   │   └── __componentBase.py
│   │   │   ├── page/
│   │   │   │   └── __page.py
│   │   │   └── workspace/
│   │   │       └── __workspace.py
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
└── typings/
    └── __builtins__.pyi
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

src/fluxCore/devices:
	__scrcpy.py - 
		CLASSE(S):
			SCRCPY -> : scrcpy

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

src/fluxCore/device:
	__device.py - 
		CLASSE(S):
			Device -> : device

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

src/fluxCore/action/android/gesture:
	__tap.py - 
		CLASSE(S):
			Tap -> : tap
	__touch.py - 
		CLASSE(S):
			Touch -> : touch

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

src/fluxCore/types/interface/devices:
	__scrcpy.py - 
		CLASSE(S):
			iSCRCPY -> : iscrcpy

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

src/fluxCore/types/interface/geometry:
	__geoBase.py - 
		CLASSE(S):
			iGeometry -> : igeometry
	__point.py - 
		CLASSE(S):
			iPoint -> : ipoint

src/fluxCore/types/interface/device:
	__device.py - 
		CLASSE(S):
			iDevice -> : idevice

src/fluxCore/types/interface/action:
	__actionMetadata.py - 
		CLASSE(S):
			iActionMetadata -> : iactionmetadata
		CONSTANTS(S)/GLOBAL(S)
			DEVICE_MINIMUM_WAIT -> : device_minimum_wait
	__androidAction.py - 
		CLASSE(S):
			iAndroidAction -> : iandroidaction

src/fluxCore/types/interface/packets:
	__frame.py - 
		CLASSE(S):
			iFrame -> : iframe
	__packet.py - 
		CLASSE(S):
			iPacket -> : ipacket

src/fluxCore/types/interface/emitters:
	__SCRCPYEmitter.py - 
		CLASSE(S):
			iSCRCPYEmitter -> : iscrcpyemitter

src/fluxCore/types/packets:
	__frame.py - 
		CLASSE(S):
			Frame -> : frame
	__packet.py - 
		CLASSE(S):
			Packet -> : packet

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

src/eNuts/UI/windows:
	__mainWindow.py - 
		CLASSE(S):
			MainWindow -> : mainwindow

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

src/eNuts/application:
	__eNutsApplication.py - 
		CLASSE(S):
			eNutsApplication -> : enutsapplication
		CONSTANTS(S)/GLOBAL(S)
			CONFIG_DIR -> : config_dir
	__eNutsService.py - 
		CLASSE(S):
			Service -> : service
	__shell.py - 
		CLASSE(S):
			Shell -> : shell

src/eNuts/application/theme:
	__theme.py - 
		FUNCTION(S):
			loadStyles -> : loadstyles
			loadStyle -> : loadstyle
			_loadPalette -> : _loadpalette

src/eNuts/apps:
	main.py - 
		FUNCTION(S):
			main -> : main
			program -> : program
	training.py - 
		FUNCTION(S):
			training -> : training
			program -> : program

src/eNuts/types/interface/application:
	__enutsService.py - 
		CLASSE(S):
			iENUTSService -> : ienutsservice
	__shell.py - 
		CLASSE(S):
			iShell -> : ishell

src/eNuts/types/interface/configuration:
	__eNutsConfiguration.py - 
		CLASSE(S):
			iENUTSConfiguration -> : ienutsconfiguration

src/eNuts/configuration:
	__eNutsConfiguration.py - 
		CLASSE(S):
			eNutsConfiguration -> : enutsconfiguration
		CONSTANTS(S)/GLOBAL(S)
			CONFIG_PATH -> : config_path
	__information.py - 
		CLASSE(S):
			ApplicationInformation -> : applicationinformation

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

src/jAGFx/logging/filters:
	__namespaceFilter.py - 
		CLASSE(S):
			NamespaceFilter -> : namespacefilter

src/jAGFx/logging/handlers:
	__dateRotatingFileHandler.py - 
		CLASSE(S):
			DateRotatingFileHandler -> : daterotatingfilehandler
	__dynamicQueueHandler.py - 
		CLASSE(S):
			DynamicQueueHandler -> : dynamicqueuehandler

src/jAGFx/logging/data:
	__baseSourceInformation.py - 
		CLASSE(S):
			BaseSourceInformation -> : basesourceinformation
	__callerInformation.py - 
		CLASSE(S):
			CallerInformation -> : callerinformation

src/jAGFx/logging/formatters:
	__defaultFormatter.py - 
		CLASSE(S):
			DefaultFormatter -> : defaultformatter
		CONSTANTS(S)/GLOBAL(S)
			C_LOG_FORMAT -> : c_log_format
			C_LOG_COLORS -> : c_log_colors
			C_SECONDARY_COLORS -> : c_secondary_colors
			fmtList -> : fmtlist

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

src/jAGFx/collections:
	__tsDictionary.py - 
		CLASSE(S):
			TSDictionary -> : tsdictionary
	__tsList.py - 
		CLASSE(S):
			TSList -> : tslist

src/jAGFx/names:
	__helpers.py - 
		FUNCTION(S):
			getRandomName -> : getrandomname
			resetNames -> : resetnames
			name -> : name
	__names.py - 
		CLASSE(S):
			_names -> : _names

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

src/jAGFx/types/interface/logger:
	__sourceInformation.py - 
		CLASSE(S):
			iSourceInformation -> : isourceinformation

src/jAGFx/types/interface/communication:
	__IOQueue.py - 
		CLASSE(S):
			iIOQueue -> : iioqueue
	__message.py - 
		CLASSE(S):
			iMessage -> : imessage

src/jAGFx/types/interface/services:
	__services.py - 
		CLASSE(S):
			iService -> : iservice
	__subscription.py - 
		CLASSE(S):
			iSubscription -> : isubscription

src/jAGFx/types/interface/serializer:
	__serializable.py - 
		CLASSE(S):
			iSerializable -> : iserializable

src/jAGFx/types/interface/configuration:
	__applicationConfiguration.py - 
		CLASSE(S):
			iApplicationConfiguration -> : iapplicationconfiguration
	__configuration.py - 
		CLASSE(S):
			iConfiguration -> : iconfiguration

src/jAGFx/configuration:
	__applicationConfig.py - 
		CLASSE(S):
			ApplicationConfiguration -> : applicationconfiguration
		CONSTANTS(S)/GLOBAL(S)
			CFGINSTANCE -> : cfginstance
			LOGGER_SECTION -> : logger_section
			CONFIG_PATH -> : config_path
			CONFIG_FILENAME -> : config_filename
			ConfigType -> : configtype
	__configuration.py - 
		CLASSE(S):
			Configuration -> : configuration

src/jAGFx/globals:
	serializer.py - 
		CONSTANTS(S)/GLOBAL(S)
			KNOWN_TYPES -> : known_types

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

src/jAGQt/window:
	__mainWindowBase.py - 
		CLASSE(S):
			MainWindowBase -> : mainwindowbase

src/jAGQt/window/windowBase:
	__windowBase.py - 
		CLASSE(S):
			WindowBase -> : windowbase

src/jAGQt/types/interface/components:
	__componentBase.py - 
		CLASSE(S):
			iComponentBase -> : icomponentbase

src/jAGQt/types/interface/window:
	__mainWindowBase.py - 
		CLASSE(S):
			iMainWindowBase -> : imainwindowbase

src/jAGQt/types/interface/window/windowBase:
	__windowBase.py - 
		CLASSE(S):
			iWindowBase -> : iwindowbase

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

src/jAGQt/widgets:
	__header.py - 
		CLASSE(S):
			Header -> : header

src/jAGQt/widgets/components:
	__componentBase.py - 
		CLASSE(S):
			ComponentBase -> : componentbase

src/jAGQt/widgets/Image:
	__image.py - 
		CLASSE(S):
			Image -> : image
			_GLView -> : _glview
		CONSTANTS(S)/GLOBAL(S)
			Backend -> : backend

src/jAGQt/widgets/SideBar:
	__sideBar.py - 
		CLASSE(S):
			DockPosition -> : dockposition
			SideBar -> : sidebar

src/jAGQt/widgets/SideBar/components:
	__sideBarContent.py - 
		CLASSE(S):
			SideBarContent -> : sidebarcontent
	__sideBarGroup.py - 
		CLASSE(S):
			SideBarGroupHeader -> : sidebargroupheader
			SideBarGroup -> : sidebargroup
	__sideBarHeader.py - 
		CLASSE(S):
			SideBarHeader -> : sidebarheader
	__sideBarIcon.py - 
		CLASSE(S):
			SideBarIcon -> : sidebaricon
	__sideBarItem.py - 
		CLASSE(S):
			ItemDisplayMode -> : itemdisplaymode
			IconPosition -> : iconposition
			SideBarItem -> : sidebaritem
	__sideBarSeparator.py - 
		CLASSE(S):
			SeparatorType -> : separatortype
			SideBarSeparator -> : sidebarseparator
	__sideBarText.py - 
		CLASSE(S):
			SideBarText -> : sidebartext

src/jAGQt/widgets/page:
	__page.py - 
		CLASSE(S):
			Page -> : page

src/jAGQt/widgets/workspace:
	__workspace.py - 
		CLASSE(S):
			Workspace -> : workspace

src/jAGQt/widgets/commandBar:
	__base.py - 
		CLASSE(S):
			_commandBarBase -> : _commandbarbase
		CONSTANTS(S)/GLOBAL(S)
			QtPolicy -> : qtpolicy
	__commandBar.py - 
		CLASSE(S):
			CommandBar -> : commandbar
		CONSTANTS(S)/GLOBAL(S)
			QtPolicy -> : qtpolicy
	__commandBarGroup.py - 
		CLASSE(S):
			CommandBarGroup -> : commandbargroup

src/jAGQt/widgets/commandBar/commandBarButton:
	__base.py - 
		CLASSE(S):
			_commandBarButtonBase -> : _commandbarbuttonbase
	__commandBarButton.py - 
		CLASSE(S):
			CommandBarButton -> : commandbarbutton

```

---

## Change Summary

```text
9025411:
	Merge branch 'development' of https://github.com/IAmJAG/eNuts into development

e57fb4d:
	feat: Implement Color class and integrate into application structure
		src/__monkeyPatch.py
		src/eNuts/application/__eNutsApplication.py
		src/jAGFx/types/__color.py
		typings/__builtins__.pyi

86d6c66:
	docs: update inventory.md using utility script
		.docs/inventory.md

266012a:
	Remove legacy theme files and implement new theme system architecture
		.docs/themeSpecification.md
		config/eNuts/dark.qss
		config/eNuts/dracula.qss
		config/eNuts/ironman.qss
		config/eNuts/light.qss
		config/eNuts/material.qss
		src/eNuts/application/theme/__theme.py
		src/eNuts/apps/main.py
		src/eNuts/configuration/__eNutsConfiguration.py
		src/eNuts/types/interface/configuration/__eNutsConfiguration.py

cff5658:
	docs: update inventory.md using utility script
		.docs/inventory.md

e4ca3c4:
	feat: Enhance inventory update script and add coding style documentation
		.docs/inventory.md
		.kilocode/rules/CodingStyle.md
		.kilocode/rules/Documentation.md
		.kilocode/rules/NamingConventions.md
		.kilocode/templates/documentTemplates.md
		.scripts/updateInventory.py

5580ac4:
	docs: update inventory.md using utility script
		.docs/inventory.md

9744238:
	Merge branch 'development' of https://github.com/IAmJAG/eNuts into development

47b8e0b:
	fix: add additional excluded directories and update inventory generation logic
		.scripts/updateInventory.py

9f319a8:
	docs: update inventory.md using utility script
		.docs/inventory.md

```