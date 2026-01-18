import { QuartzConfig } from "./quartz/cfg"
import * as Plugin from "./quartz/plugins"

/**
 * Quartz 4 Configuration
 *
 * See https://quartz.jzhao.xyz/configuration for more information.
 */
const config: QuartzConfig = {
  configuration: {
    pageTitle: "Tom's Notes",
    pageTitleSuffix: "",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: "tomboo.github.io/quartz-site",
    ignorePatterns: [
      "_framework/**",
      ".obsidian/**",
      "tmp/**",
      ".cache/**",
      "*.base",
      // Private content
      "_database/database-core/sessions-table/**",
      "_database/database-core/tasks-table/**",
      "_database/database-core/backlog-table/**",
      "_database/database-core/daily-notes-table/**",
    ],
    defaultDateType: "modified",
    theme: {
      fontOrigin: "googleFonts",
      cdnCaching: true,
      typography: {
        header: "Inter",
        body: "Inter",
        code: "JetBrains Mono",
      },
      colors: {
        lightMode: {
          light: "#ffffff",
          lightgray: "#f0f0f0",
          gray: "#999999",
          darkgray: "#333333",
          dark: "#1a1a1a",
          secondary: "#007aff",
          tertiary: "#5ac8fa",
          highlight: "rgba(0, 122, 255, 0.08)",
          textHighlight: "#007aff22",
        },
        darkMode: {
          light: "#1c1c1e",
          lightgray: "#2c2c2e",
          gray: "#636366",
          darkgray: "#ebebf5",
          dark: "#ffffff",
          secondary: "#0a84ff",
          tertiary: "#64d2ff",
          highlight: "rgba(10, 132, 255, 0.12)",
          textHighlight: "#0a84ff33",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({
        priority: ["frontmatter", "git", "filesystem"],
      }),
      Plugin.SyntaxHighlighting({
        theme: {
          light: "github-light",
          dark: "github-dark",
        },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
      Plugin.Latex({ renderEngine: "katex" }),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({
        enableSiteMap: true,
        enableRSS: true,
      }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
      // Comment out CustomOgImages to speed up build time
      Plugin.CustomOgImages(),
    ],
  },
}

export default config
