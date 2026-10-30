# 面向使用者的 README 生成

仅在创建或实质调整根 README 时读取。采用 `create-readme` 的创作思路：先理解整个项目，再把项目价值、结构与使用路径组织成清晰入口。此参考随套件提供，不要求业务环境额外安装该技能，也不把它变成第六个默认入口。

## 先调查，再写

查看现有说明、主要目录、构建与依赖清单、入口、核心实现、测试和配置，识别项目类型、使用者、成熟度、代表性场景与已知约束。整体覆盖、重点深入，不为写 README 全量读取文件或反编译所有依赖。

使用 [README 模板](../assets/templates/readme.md) 组织输出。先说明项目用途与核心能力，再用图解释结构和运行/使用过程，提供最短上手路径与验证命令，最后导航到细节。README 本身应足以建立项目基本理解；Wiki 承载更深入的模块、契约、规则与来源说明。

## 图解选择与证据

对于存在相应结构和交互的项目，默认提供整体架构图、代表性业务/能力流程图和关键交互时序图。三个图应回答不同问题，不把同一条流水线换三种画法重复展示。

涉及图解时读取 [通用图解规则](diagram-guidance.md)，按阅读问题选择图，并核实节点、关系、顺序及边界。该规则同样用于 Wiki 专题的新增、更新与维护。

简单工具没有独立运行交互时不硬凑时序图。概览图放 README，复杂子流程放专题后链接，避免为了完整性把 README 写成所有细节的汇总。

## 内容与表达

- 用 GFM；已有项目 Logo/图标时可复用页首，不凭空生成徽章、构建状态、截图或性能数据。
- 核心能力用场景与结果描述。短示例和可观察的首次运行结果优先于大段参数手册。
- 前置条件、配置、构建、启动与测试取自项目事实；标清存在的命令和实际验证结果，不为写文档擅自部署或连接生产资源。
- 不过量使用 emoji。GFM 提示块仅用于会影响使用决定的真实条件，避免重复警告。
- LICENSE、CONTRIBUTING、CHANGELOG 等信息由各自文件维护，不另起同名章节重复。
- 只链接实际文件。模板提示、空表、空图和未替换占位符不进入交付文档。

## 风格参考

以下 README 用于参考项目价值、架构说明、示例、快速开始与导航的组织方式；不复制技术栈、云部署步骤或全部章节：

- [Serverless Chat](https://raw.githubusercontent.com/Azure-Samples/serverless-chat-langchainjs/refs/heads/main/README.md)
- [Serverless Recipes](https://raw.githubusercontent.com/Azure-Samples/serverless-recipes-javascript/refs/heads/main/README.md)
- [run-on-output](https://raw.githubusercontent.com/sinedied/run-on-output/refs/heads/main/README.md)
- [smoke](https://raw.githubusercontent.com/sinedied/smoke/refs/heads/main/README.md)
