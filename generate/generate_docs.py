"""scrapli_cfg.docs.generate"""
import pdoc
from pdoc import _render_template, tpl_lookup

context = pdoc.Context()
module = pdoc.Module("scrapli_cfg", context=context)
pdoc.link_inheritance(context)
tpl_lookup.directories.insert(0, "docs/generate")

doc_map = {
    "scrapli_cfg.platform.base.async_platform": {
        "path": "platform/base/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.base.base_platform": {
        "path": "platform/base/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.base.sync_platform": {
        "path": "platform/base/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.arista_eos.async_platform": {
        "path": "platform/core/arista_eos/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.arista_eos.base_platform": {
        "path": "platform/core/arista_eos/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.arista_eos.sync_platform": {
        "path": "platform/core/arista_eos/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.arista_eos.patterns": {
        "path": "platform/core/arista_eos/patterns",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxe.async_platform": {
        "path": "platform/core/cisco_iosxe/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxe.base_platform": {
        "path": "platform/core/cisco_iosxe/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxe.sync_platform": {
        "path": "platform/core/cisco_iosxe/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxe.patterns": {
        "path": "platform/core/cisco_iosxe/patterns",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxr.async_platform": {
        "path": "platform/core/cisco_iosxr/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxr.base_platform": {
        "path": "platform/core/cisco_iosxr/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxr.sync_platform": {
        "path": "platform/core/cisco_iosxr/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_iosxr.patterns": {
        "path": "platform/core/cisco_iosxr/patterns",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_nxos.async_platform": {
        "path": "platform/core/cisco_nxos/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_nxos.base_platform": {
        "path": "platform/core/cisco_nxos/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_nxos.sync_platform": {
        "path": "platform/core/cisco_nxos/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.cisco_nxos.patterns": {
        "path": "platform/core/cisco_nxos/patterns",
        "content": None,
    },
    "scrapli_cfg.platform.core.juniper_junos.async_platform": {
        "path": "platform/core/juniper_junos/async_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.juniper_junos.base_platform": {
        "path": "platform/core/juniper_junos/base_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.juniper_junos.sync_platform": {
        "path": "platform/core/juniper_junos/sync_platform",
        "content": None,
    },
    "scrapli_cfg.platform.core.juniper_junos.patterns": {
        "path": "platform/core/juniper_junos/patterns",
        "content": None,
    },
    "scrapli_cfg.diff": {"path": "diff", "content": None},
    "scrapli_cfg.exceptions": {"path": "exceptions", "content": None},
    "scrapli_cfg.factory": {"path": "factory", "content": None},
    "scrapli_cfg.logging": {"path": "logging", "content": None},
    "scrapli_cfg.response": {"path": "response", "content": None},
}


def recursive_mds(module):  # noqa
    """Recursively render mkdocs friendly markdown/html"""
    yield module.name, _render_template("/mkdocs_markdown.mako", module=module)
    for submod in module.submodules():
        yield from recursive_mds(submod)


def main():
    """Generate docs"""
    for module_name, html in recursive_mds(module=module):
        if module_name not in doc_map.keys():
            continue

        doc_map[module_name]["content"] = html

    for module_name, module_doc_data in doc_map.items():
        if not module_doc_data["content"]:
            print(f"broken module {module_name}")
            continue
        with open(f"docs/api_docs/{module_doc_data['path']}.md", "w") as f:
            f.write(module_doc_data["content"])


if __name__ == "__main__":
    main()
