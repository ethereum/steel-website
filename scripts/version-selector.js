// Custom version selector for multi-depth branch paths.
//
// Material's built-in selector (provider: mike) breaks for our URL structure
// because it extracts only the last path segment and uses relative navigation.
// This script uses absolute paths throughout and is injected during deploy.
(function () {
  "use strict";

  var DOCS_PREFIX = "/docs/";
  var VERSIONS_URL = DOCS_PREFIX + "versions.json";

  // Find the current version by matching location.pathname against known paths.
  // Longest match wins (so "devnets/amsterdam/2" beats "devnets/amsterdam").
  function findCurrentVersion(versions) {
    var path = location.pathname;
    var best = null;
    for (var i = 0; i < versions.length; i++) {
      var prefix = DOCS_PREFIX + versions[i].version + "/";
      if (path.startsWith(prefix)) {
        if (!best || versions[i].version.length > best.version.length) {
          best = versions[i];
        }
      }
    }
    return best;
  }

  function buildSelector(versions, current) {
    // Use Material's own CSS classes so styling is native.
    var container = document.createElement("div");
    container.className = "md-version";

    var btn = document.createElement("button");
    btn.className = "md-version__current";
    btn.setAttribute("aria-label", "Select version");
    btn.textContent = current ? current.title : "Select version";

    if (current && current.aliases && current.aliases.length > 0) {
      var aliasSpan = document.createElement("span");
      aliasSpan.className = "md-version__alias";
      aliasSpan.textContent = current.aliases[0];
      btn.appendChild(aliasSpan);
    }

    var list = document.createElement("ul");
    list.className = "md-version__list";

    for (var i = 0; i < versions.length; i++) {
      var v = versions[i];
      var li = document.createElement("li");
      li.className = "md-version__item";

      var a = document.createElement("a");
      a.className = "md-version__link";
      a.href = v.url || (DOCS_PREFIX + v.version + "/");
      a.textContent = v.title;

      if (v.aliases && v.aliases.length > 0) {
        var alias = document.createElement("span");
        alias.className = "md-version__alias";
        alias.textContent = v.aliases[0];
        a.appendChild(alias);
      }

      li.appendChild(a);
      list.appendChild(li);
    }

    container.appendChild(btn);
    container.appendChild(list);
    return container;
  }

  function inject(versions, current) {
    var target = document.querySelector(".md-header__topic");
    if (!target) return;

    // Remove Material's built-in (broken) selector if it rendered.
    var existing = target.querySelector(".md-version");
    if (existing) existing.remove();

    target.appendChild(buildSelector(versions, current));
  }

  function init() {
    if (!location.pathname.startsWith(DOCS_PREFIX)) return;

    fetch(VERSIONS_URL)
      .then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      })
      .then(function (versions) {
        inject(versions, findCurrentVersion(versions));
      })
      .catch(function () {
        // Silent -- same behaviour as Material's built-in.
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
