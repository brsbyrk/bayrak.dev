import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import astroParser from "astro-eslint-parser";
import eslintPluginAstro from "eslint-plugin-astro";

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...eslintPluginAstro.configs.recommended,
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
  },
  {
    files: ["*.astro"],
    languageOptions: {
      parser: astroParser,
      parserOptions: {
        parser: "@typescript-eslint/parser",
        extraFileExtensions: [".astro"],
      },
    },
  },
  {
    files: ["tailwind.config.cjs", "**/*.d.ts"],
    rules: {
      "@typescript-eslint/no-require-imports": "off",
      "@typescript-eslint/triple-slash-reference": "off",
      "@typescript-eslint/no-unused-vars": "off",
    },
  },
  {
    rules: {
      "@typescript-eslint/no-unused-expressions": "off",
    },
  },
  {
    ignores: ["dist/**", ".astro"],
  },
];
