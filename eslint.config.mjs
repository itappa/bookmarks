import pluginTailwindCss from 'eslint-plugin-tailwindcss';

export default [
  {
    plugins: {
      tailwindcss: pluginTailwindCss
    },
    rules: {
      // Tailwindのクラス名の並び替えのみを有効にする
      'tailwindcss/classnames-order': 'warn',
    },
    settings: {
      tailwindcss: {
        // 必要に応じてTailwind CSSの設定ファイルのパスを指定
        // config: 'path/to/your/tailwind.config.js',
      }
    }
  }
];