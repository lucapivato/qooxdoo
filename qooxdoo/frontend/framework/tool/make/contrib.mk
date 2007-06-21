CONTRIB_UTIL = $(CMD_PYTHON) $(FRAMEWORK_TOOL_PATH)/contrib.py

ifneq ($(APPLICATION_INCLUDES),)
	MANIFESTS = $(patsubst %, --manifest %/Manifest.js , $(APPLICATION_INCLUDES))	
	
	APPLICATION_ADDITIONAL_CLASS_PATH += $(shell $(CONTRIB_UTIL) $(MANIFESTS) --class-path)
	APPLICATION_ADDITIONAL_CLASS_URI += $(shell $(CONTRIB_UTIL) $(MANIFESTS) --class-uri)
	
	APPLICATION_ADDITIONAL_BUILD_OPTIONS += $(shell $(CONTRIB_UTIL) $(MANIFESTS) --resource-flags-build)
	APPLICATION_ADDITIONAL_SOURCE_OPTIONS += $(shell $(CONTRIB_UTIL) $(MANIFESTS) --resource-flags-source)
endif
