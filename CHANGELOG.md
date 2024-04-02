# [v0.8.0](https://github.com/haliphax/xthulu/compare/v0.7.0...v0.8.0) (2024-04-02)

## ✨ New Features
- [`9de58d6`](https://github.com/haliphax/xthulu/commit/9de58d6)  command line flags for db commands 
- [`13a1286`](https://github.com/haliphax/xthulu/commit/13a1286)  submit messages filter modal with enter key 
- [`a64b7b7`](https://github.com/haliphax/xthulu/commit/a64b7b7)  setup script

# [v0.7.0](https://github.com/haliphax/xthulu/compare/v0.6.0...v0.7.0) (2024-03-28)

## ✨ New Features
- [`08082ce`](https://github.com/haliphax/xthulu/commit/08082ce)  enter submits message details modal 
- [`d5f5c35`](https://github.com/haliphax/xthulu/commit/d5f5c35)  scrollable messages list 
- [`c67023d`](https://github.com/haliphax/xthulu/commit/c67023d)  main menu 
- [`f063a94`](https://github.com/haliphax/xthulu/commit/f063a94)  reject bad_usernames entries during login 
- [`9ef3f44`](https://github.com/haliphax/xthulu/commit/9ef3f44)  log to file

# [v0.6.0](https://github.com/haliphax/xthulu/compare/v0.5.1...v0.6.0) (2024-03-27)

## ✨ New Features
- [`5a51480`](https://github.com/haliphax/xthulu/commit/5a51480)  filter messages by tags

# [v0.5.1](https://github.com/haliphax/xthulu/compare/v0.5.0...v0.5.1) (2024-03-27)

## 🐛 Bug Fixes
- [`0040c67`](https://github.com/haliphax/xthulu/commit/0040c67)  fix build-web script by setting HOME env var to /tmp

# [v0.5.0](https://github.com/haliphax/xthulu/compare/v0.4.0...v0.5.0) (2024-03-27)

## ✨ New Features
- [`0e0c616`](https://github.com/haliphax/xthulu/commit/0e0c616)  typescript web userland 
- [`65d1e50`](https://github.com/haliphax/xthulu/commit/65d1e50)  basic public message system (#117) (Issues: [`#117`](https://github.com/haliphax/xthulu/issues/117))

## 🐛 Bug Fixes
- [`6d3f2cc`](https://github.com/haliphax/xthulu/commit/6d3f2cc)  256/truecolor detection fix

# [v0.4.0](https://github.com/haliphax/xthulu/compare/v0.3.1...v0.4.0) (2023-10-23)

## ✨ New Features
- [`5fd8ca3`](https://github.com/haliphax/xthulu/commit/5fd8ca3)  logoff script 

## 🐛 Bug Fixes
- [`2aba3e6`](https://github.com/haliphax/xthulu/commit/2aba3e6)  fix web auth db bind 

## 🔒 Security Issues
- [`3025950`](https://github.com/haliphax/xthulu/commit/3025950) ️ CSRF for web chat

# [v0.3.1](https://github.com/haliphax/xthulu/compare/v0.3.0...v0.3.1) (2023-10-18)

## 🐛 Bug Fixes
- [`e89ec41`](https://github.com/haliphax/xthulu/commit/e89ec41)  ensure database connections are closed 
- [`510715d`](https://github.com/haliphax/xthulu/commit/510715d)  ensure ssh db connection is open :P 
- [`552370e`](https://github.com/haliphax/xthulu/commit/552370e)  html-encode chat messages

# [v0.3.0](https://github.com/haliphax/xthulu/compare/v0.2.0...v0.3.0) (2023-10-18)

## ✨ New Features
- [`7b408ef`](https://github.com/haliphax/xthulu/commit/7b408ef)  switch from Flask to FastAPI for server-sent events; web chat

# [v0.2.0](https://github.com/haliphax/xthulu/compare/v0.1.0...v0.2.0) (2023-10-17)

## ✨ New Features
- [`ab976f0`](https://github.com/haliphax/xthulu/commit/ab976f0)  node chat script

# [v0.1.0](https://github.com/haliphax/xthulu/compare/v0.0.2...v0.1.0) (2023-10-17)

## ✨ New Features
- [`d0b74a9`](https://github.com/haliphax/xthulu/commit/d0b74a9)  window titles
- [`41f1ad5`](https://github.com/haliphax/xthulu/commit/41f1ad5)  load version dynamically in top
- [`2021e48`](https://github.com/haliphax/xthulu/commit/2021e48)  BannerApp wrapper class

# v0.0.3 (2023-10-13)

## Fix

* 🔧 fix postgres port in example config ([`8873acf`](https://github.com/haliphax/xthulu/commit/8873acf432b4f2aa0e53450141aea03d601fcce9))

* 🩹 fix double reversal of oneliners ([`31c9c28`](https://github.com/haliphax/xthulu/commit/31c9c28d4b4e570438a856d7714501fd82a1ed0a))

* 📝 fix db commands in readme ([`59a248c`](https://github.com/haliphax/xthulu/commit/59a248c66046c66c4876e2084aff00b7c55b54b3))

## Other

* ⏪️ revert to secrets-provided token due to branch protections ([`9afec3c`](https://github.com/haliphax/xthulu/commit/9afec3cec2c1af779664ca22685f5f1352f65b82))

* 🧑‍💻 moar pre-commit hooks ([`f4991d2`](https://github.com/haliphax/xthulu/commit/f4991d2a953add7c60f5d1206463a5f00206bb85))

* 👷 update version of checkout action in workflows ([`97a32b0`](https://github.com/haliphax/xthulu/commit/97a32b05c4086c7e57edd54429e92fd86e8be963))

* 👷 force patch release until 0.1.0 ([`5988be5`](https://github.com/haliphax/xthulu/commit/5988be5dbc92ac617c831641c4a65fcbed6a0593))

* 👷 use default token for release workflow ([`0b05e49`](https://github.com/haliphax/xthulu/commit/0b05e490d1f33b36157d909798566da5ee092c7e))

* 🚨 lint LICENSE.md ([`4309466`](https://github.com/haliphax/xthulu/commit/430946653cd4b691b1331f431577803632d9551b))

* ✨ load version dynamically in top ([`41f1ad5`](https://github.com/haliphax/xthulu/commit/41f1ad5a2b1cfe4ede7e695a3ba05292f125a30b))

* 🩹 explicit utf-8 check in top ([`fc2a0ab`](https://github.com/haliphax/xthulu/commit/fc2a0ab53d7f57a122049eb6e50dfb9c2d121863))

* 🚚 LICENSE -&gt; LICENSE.md ([`788b1ff`](https://github.com/haliphax/xthulu/commit/788b1ff3758b46fcda11c7988068b77d5367c5af))

* ⚡️ reverse oneliners in database vs. python ([`b7a4bc6`](https://github.com/haliphax/xthulu/commit/b7a4bc6e40d14e3b79f3371a0af9b697431b0644))

* ✅ tiny test reorg ([`2eea2e1`](https://github.com/haliphax/xthulu/commit/2eea2e1ff659a48115518f14a1ec9b40972fb945))

* ✨ window titles ([`d0b74a9`](https://github.com/haliphax/xthulu/commit/d0b74a989defc1affd1c972108e11131f295d2bf))


# v0.0.2 (2023-10-13)

## Fix

* 💚 fix semantic-release publishing settings ([`fd808a8`](https://github.com/haliphax/xthulu/commit/fd808a81449802312ff72813f96f6e3a2d9b9559))

* 🩹 fix cropping in art display methods ([`c87c531`](https://github.com/haliphax/xthulu/commit/c87c53168e8b94f4cfcb7ef6ef4ef2e66f9623fc))

* 🩹 fix oneliners banner crop ([`d915da4`](https://github.com/haliphax/xthulu/commit/d915da4cd29ca52071a664d7c78aa65317801488))

* 🧑‍💻 fix dev containers (sort of) ([`de97edc`](https://github.com/haliphax/xthulu/commit/de97edccc743975c6289192fad4095caf37a2fd5))

* 💄 amiga codec fixups ([`364b470`](https://github.com/haliphax/xthulu/commit/364b47036e8e2668022241591fa0d4fceb226523))

* 🩹 fix oneliner loading ([`c191a85`](https://github.com/haliphax/xthulu/commit/c191a85cdef5234416820ebd88ced7c385cf844d))

* ✏️ fix ports in docker-compose ([`865a9f2`](https://github.com/haliphax/xthulu/commit/865a9f29b2c18ca836ec9058b963ffbadbd5c641))

* ⬆️ bump pyaml to 6.0.1 to fix docker build ([`d48ad95`](https://github.com/haliphax/xthulu/commit/d48ad9522042092bc0d0239060dfa16e25d32e64))

* 💚 fix docker-compose restart parameter (#97) ([`fd3e32b`](https://github.com/haliphax/xthulu/commit/fd3e32b8ecf9a9a321e09398c4d823f2e163e9d3))

* fix requirements.in source file (#89) ([`8e1ffc2`](https://github.com/haliphax/xthulu/commit/8e1ffc29a8b615c69e03943708c26c08e5d27dd9))

* fix github workflow change detection and pin ruff/black to py311 (#73) ([`6599c89`](https://github.com/haliphax/xthulu/commit/6599c895dd716728e853cb56149871bd047bb5cd))

* fix userland seed imports ([`47f13e3`](https://github.com/haliphax/xthulu/commit/47f13e3dc1c27b5a56523ae9e481917d8ada6412))

* queue fixups ([`f881fcb`](https://github.com/haliphax/xthulu/commit/f881fcb9e2e15ca74cd11cfddf68b6d02716c8de))

* contributor guide fixups ([`6484f72`](https://github.com/haliphax/xthulu/commit/6484f7253be3f8f5926425538ae126bea7fbd5b6))

* cli fixes ([`f4fa8d6`](https://github.com/haliphax/xthulu/commit/f4fa8d6e1ed3cd6995f41b6196153ac3a064b7c9))

* fix end-of-line check in block editor kp_end ([`ea1ea59`](https://github.com/haliphax/xthulu/commit/ea1ea595b68a525390f72533666e8e5e43628ed3))

* fix tests ([`b004f36`](https://github.com/haliphax/xthulu/commit/b004f362b70b7e37ea34c60b1d9cbd5b9525f157))

* userland import fixes ([`f18abbf`](https://github.com/haliphax/xthulu/commit/f18abbf9943973d6598590082ecae4de5bb30dba))

* fix import in tests ([`ee0c78c`](https://github.com/haliphax/xthulu/commit/ee0c78c33723611699b50d79c2114c3cec302ea7))

* fix formatting of python block ([`1240319`](https://github.com/haliphax/xthulu/commit/12403199631a6670bb40ebb5d34c5d32e90e574a))

* fix coverage command ([`8ab8c46`](https://github.com/haliphax/xthulu/commit/8ab8c4661494f35a13d6f66c19f5a7c9b17c28c4))

* fix awkward wording ([`eb5b62d`](https://github.com/haliphax/xthulu/commit/eb5b62d96fa3ca23278b24b7acccbf5a75e14eca))

* fix test imports ([`6565b48`](https://github.com/haliphax/xthulu/commit/6565b485eb5ac6b398291a73e14990bf34b609cb))

* fix exception logging in connection_lost ([`8aadabd`](https://github.com/haliphax/xthulu/commit/8aadabdb9b8f24b5924d76578efcc791abd86363))

* proxy terminal fixups ([`81fec9a`](https://github.com/haliphax/xthulu/commit/81fec9a9f3f10003f542d999e365a7c742bf4d48))

* import fixups ([`2b72ac0`](https://github.com/haliphax/xthulu/commit/2b72ac044d870ffcedc747e21f9e9dea1e84c102))

* fix tests ([`91c21f3`](https://github.com/haliphax/xthulu/commit/91c21f30a57f0008f4266f50ce7afd58528f58f0))

* more type hints and docstring fixes ([`158a36b`](https://github.com/haliphax/xthulu/commit/158a36be4fc40a1b05a935480c54fbb908d150c6))

* fix broken import ([`ffad0c6`](https://github.com/haliphax/xthulu/commit/ffad0c63f72df32c24afd71e21f9808c5f165c91))

* fix show_art (a bit more) ([`2e53def`](https://github.com/haliphax/xthulu/commit/2e53def604776ee8b3f131064eaacadf66298abd))

* fix show_art (mostly) ([`8223a93`](https://github.com/haliphax/xthulu/commit/8223a932c3a63c28cfc6991060e2431c71d6a356))

* more type check fixes ([`1c36846`](https://github.com/haliphax/xthulu/commit/1c3684650cfeadcf880c001b3788ce1f2630e512))

* lint fixes ([`c04ca12`](https://github.com/haliphax/xthulu/commit/c04ca12b8a025fca7992b2a096f240ec4478e89d))

* fix indent ([`20c91be`](https://github.com/haliphax/xthulu/commit/20c91bed6b266902053385d82fc79bb320f31a02))

* overhaul: python 3.11, docker improvements, fixups, dev experience ([`19541e5`](https://github.com/haliphax/xthulu/commit/19541e56d4d1aad7de63197ca64fd61db0fdaeb6))

* fix asyncio exception references ([`fdc175f`](https://github.com/haliphax/xthulu/commit/fdc175fad244903ff605c816234323fe2f51fd52))

* fix wrapping until limit ([`ca2621a`](https://github.com/haliphax/xthulu/commit/ca2621a10da22e7928bc3ce38c85f2e34e157838))

* fix last-login datetime issue ([`ab6809f`](https://github.com/haliphax/xthulu/commit/ab6809f48be657985f9a262ab49c9838ca968fa0))

* fixed levelname width in log output ([`3d2165e`](https://github.com/haliphax/xthulu/commit/3d2165e1c221c803e2f04fce9730637722655c85))

* proc is still in scope, no need for cx prefix ([`df5aa0b`](https://github.com/haliphax/xthulu/commit/df5aa0be29a027c8e50334f717a44ba1edee5540))

* fix PIPE type hints ([`7684baf`](https://github.com/haliphax/xthulu/commit/7684baf2a0fa0c86d02f0ff804b81e5621cd6737))

* fix editor value init ([`2a3639a`](https://github.com/haliphax/xthulu/commit/2a3639acca58395f625260c5a361dc24b9786f6b))

* fix wrapping for delete, etc. ([`4c0c3c9`](https://github.com/haliphax/xthulu/commit/4c0c3c970301b8e5e4464bf6839b763f6043aab6))

* fix edge of line editor ([`e53dd26`](https://github.com/haliphax/xthulu/commit/e53dd26c5896f4d48a878a1d146be1c706fb4b1e))

* incorporate jquast ProxyTerminal and blessed upgrade to fix move_* formatting strings ([`c9af2d8`](https://github.com/haliphax/xthulu/commit/c9af2d86e9a40cd55281b6385e3988418e531643))

* ui.editors.BlockEditor docstring fix ([`6a70699`](https://github.com/haliphax/xthulu/commit/6a706996af9af175f72ea57d40d77f31b0b07d75))

* Context.release_lock docstring fix ([`35c6970`](https://github.com/haliphax/xthulu/commit/35c6970924c5b295b59f8648e196b8122512c207))

* fix editor cursor/split bugs ([`5e31d6e`](https://github.com/haliphax/xthulu/commit/5e31d6e89fd81fe7b50a362ea9c6ddeeab38a9f1))

* fix term proxying ([`00df859`](https://github.com/haliphax/xthulu/commit/00df859670a8026d9a02c61ae4463b6c3be7a921))

* don&#39;t size editor according to text; always fixed row size ([`0c49343`](https://github.com/haliphax/xthulu/commit/0c49343a761576d9ec9bc493563f61dd70287e56))

* fix db permission bullshit ([`ea57f60`](https://github.com/haliphax/xthulu/commit/ea57f60ea9df48411cbfea70e560eeb8951207ff))

* termfix before session ident in top ([`76c538b`](https://github.com/haliphax/xthulu/commit/76c538bf22f68db8a236381275b2d183095e1248))

* fix lock expiration and ctx manager ([`2dfba41`](https://github.com/haliphax/xthulu/commit/2dfba419d4003c1e1f3f759329f6fee87b794406))

* fix script importing; docker compose ([`0332516`](https://github.com/haliphax/xthulu/commit/0332516822869236a2b7ee25d96350abdf2b4b1a))

* fix remaining xc.remote_ip refs ([`5f94948`](https://github.com/haliphax/xthulu/commit/5f94948a0db99af80125416f7fd812c63ae6cce1))

* fix redundant config load ([`d78f517`](https://github.com/haliphax/xthulu/commit/d78f5173b1c6e43b2dc1be44efe825375868a27a))

## Other

* 👷 point semantic-release at main branch ([`8d2a28a`](https://github.com/haliphax/xthulu/commit/8d2a28a163d0559ed83992de96124e398863c158))

* 📝 add uvicorn to readme ([`2b25215`](https://github.com/haliphax/xthulu/commit/2b2521553f0ce2b021f1f7e011372d15710ac51e))

* 💄 userland script css puffery ([`4d63628`](https://github.com/haliphax/xthulu/commit/4d63628e470c3950dc81995e26359de3999c272c))

* 💄 oneliners css overhaul ([`c44fb72`](https://github.com/haliphax/xthulu/commit/c44fb726b083c70f336c7cb50779d7254f8f5bd9))

* 🧑‍💻 textual css highlighter extension ([`b9337a5`](https://github.com/haliphax/xthulu/commit/b9337a5f7183dcf6e7fed30c25b9a4725223a039))

* 💡 oneliners docstrings ([`adbcc4f`](https://github.com/haliphax/xthulu/commit/adbcc4f842c5dcf4b983051a2151c4335b4fdd6b))

* ✅ event queue chronology tests ([`27d5e15`](https://github.com/haliphax/xthulu/commit/27d5e15a3d2652a9471cd42fcfaf80363babd2fb))

* 💡 comment test stages ([`6bd5280`](https://github.com/haliphax/xthulu/commit/6bd52808c55f117fdb9d7fc3ef3b469eeaa99b5a))

* ✅ clean up ssh server tests ([`64ec11c`](https://github.com/haliphax/xthulu/commit/64ec11cd672d452230d9b513b8fb38031f710573))

* ✅ moar event queue tests ([`3683945`](https://github.com/haliphax/xthulu/commit/3683945e8d3322102b00a2a52a2b5e2ed53c5ad5))

* 👷 workflow concurrency rules ([`ac2a684`](https://github.com/haliphax/xthulu/commit/ac2a6843e4fd3bd0f2d3d59e05d200ea6a76f108))

* ✅ event queue tests ([`e4506a9`](https://github.com/haliphax/xthulu/commit/e4506a921a0a95148211c4e5f27668f783cd28ae))

* 💄 reduce vertical spacing for locks demo banner ([`a81feca`](https://github.com/haliphax/xthulu/commit/a81feca36d7d586334b925056d82b6195ae822c5))

* ✨ add sysinfo to top demo ([`449340e`](https://github.com/haliphax/xthulu/commit/449340e8de386f22cd7be5808cb7f07235e3a3f1))

* 🎨 vim demo ([`f35f2ca`](https://github.com/haliphax/xthulu/commit/f35f2ca26be5042922d4cc7590d723a9c15ce473))

* 🧑‍💻 add even-better-toml to extension recs ([`edb0f0b`](https://github.com/haliphax/xthulu/commit/edb0f0b219afc51ea27dacbc378e3e85e116cd68))

* 🔧 update timeout in example config ([`a4e742b`](https://github.com/haliphax/xthulu/commit/a4e742bea53fc7a88db6b57361ee2b5abf377fdf))

* 💡 docstrings ([`6ab7efa`](https://github.com/haliphax/xthulu/commit/6ab7efae9a191e411982ce8c088d2c02d6e8e9b2))

* 🙈 add ruff cache to vscode ignore ([`3e9adf1`](https://github.com/haliphax/xthulu/commit/3e9adf1813c3bbdadd99343bdf79c6e0a828572e))

* 🎨 use /bin/true for base image ([`5fccf81`](https://github.com/haliphax/xthulu/commit/5fccf812c78c8367d539f20cdeef735576de5b33))

* 🦺 drop support for non-utf-8 encodings for now ([`e5351fa`](https://github.com/haliphax/xthulu/commit/e5351fa88054e4dbd2b33ac24a03bac8d33e89a6))

* ✨ extend oneliners length, inline css ([`35a55e5`](https://github.com/haliphax/xthulu/commit/35a55e577883f2ebe638183fb336e94e4b6881b8))

* 📝 update contributor guide ([`449dd60`](https://github.com/haliphax/xthulu/commit/449dd60c728228f72847af2dd881efb8ea02f319))

* 📝 docker-compose =&gt; docker compose ([`70c3fa9`](https://github.com/haliphax/xthulu/commit/70c3fa9c19958b2e40dc5ace05e6b9e3e848b75b))

* 📝 update readme links for rich/textual ([`d8854d0`](https://github.com/haliphax/xthulu/commit/d8854d0766d70100ff963d61871a9df8d698c4a4))

* ✨ improve oneliner validation ([`c62c0aa`](https://github.com/haliphax/xthulu/commit/c62c0aaf01b01efb47db45c12191cd270288c00d))

* 💄 tweak artwork ([`1f594e6`](https://github.com/haliphax/xthulu/commit/1f594e6cb4937dc4da7c5b6c4b14fa1f2078a053))

* ✨ context.inkey method ([`78712ee`](https://github.com/haliphax/xthulu/commit/78712ee200ffb7bccfe16b982283c5a9ef902580))

* 🧑‍💻 update vscode settings ([`981fef5`](https://github.com/haliphax/xthulu/commit/981fef507bed053b4056491629e8725359be65e8))

* ✨ replace blessed with rich/textual (#113) ([`e99dcb7`](https://github.com/haliphax/xthulu/commit/e99dcb7cbc168f4f63ae86d495ff243419105543))

* ⬆️ Bump gitpython from 3.1.35 to 3.1.37 in /requirements (#112)
