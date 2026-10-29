# JVM：只有 JAR 也要查证

先从当前模块构建配置和实际解析结果定位准确 JAR。使用项目现有 Maven/Gradle 工具核查依赖；命令可能解析或下载依赖，遵守当前环境权限。多模块、test/runtime scope、传递版本和多版本 JAR 均以实际目标为准。

按本次关键词查看归档目录，例如缓存或异常所在包：

```sh
python <skill-dir>/scripts/inspect_artifact.py /actual/component.jar --match Cache --limit 40
javap -classpath /actual/component.jar -public actual.package.ObservedClass
```

第二个命令的类名必须来自前一步或真实调用；示意路径不是可直接执行的 API。依赖父类或接口时补充它们的真实 classpath，核查继承接口；多版本包按目标 Java 版本选择条目，不能默认基础条目就是实际运行接口。

只在需要时查看对应方法字节码（`javap -c`）、注解/常量或局部反编译；不要把反编译还原的名字和注释当原始契约。公开方法存在也可能不属于框架承诺的稳定扩展接口。

核查相关资源：随包文档、服务注册、配置元数据和自动配置入口（仅当框架实际使用这些机制）。资源存在不等于应用中已启用，要结合配置、条件及现有调用验证。

关键语义例如 TTL 单位、null 处理、租户隔离、异常转换，通过匹配版本资料或真实组件聚焦测试确认。编译通过和 Mock 通过不代替该证据。

参考：[javap 官方文档](https://docs.oracle.com/en/java/javase/21/docs/specs/man/javap.html)。
