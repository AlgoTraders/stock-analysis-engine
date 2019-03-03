# Copyright 2017 The Openstack-Helm Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

HELM := helm
TASK := build

EXCLUDES := cron doc prometheus redis tests tools logs
CHARTS := $(filter-out $(EXCLUDES), $(patsubst %/.,%,$(wildcard */.)))

all: $(CHARTS)

$(CHARTS):
	@echo
	@echo "===== Processing [$@] chart ====="
	@make $(TASK)-$@

init-%:
	if [ -f $*/Makefile ]; then make --directory=$*; fi
	if [ -f $*/requirements.yaml ]; then helm dependency update $*; fi

lint-%: init-%
	if [ -d $* ]; then $(HELM) lint $*; fi

build-%: lint-%
	if [ -d $* ]; then $(HELM) package $*; fi

clean:
	@echo "Removed files"

.PHONY: $(EXCLUDES) $(CHARTS)
