import StyleDictionary from 'style-dictionary';

// Custom format for TypeScript with proper typing
StyleDictionary.registerFormat({
  name: 'typescript/es6-declarations',
  format: ({ dictionary }) => {
    const tokens = dictionary.allTokens;

    // Build nested object structure
    const tokenObject = {};
    tokens.forEach(token => {
      const path = token.path;
      let current = tokenObject;

      path.forEach((key, index) => {
        if (index === path.length - 1) {
          current[key] = token.value;
        } else {
          current[key] = current[key] || {};
          current = current[key];
        }
      });
    });

    return `/**
 * IES Design Tokens v2.0
 * Auto-generated from Style Dictionary
 * DO NOT EDIT MANUALLY
 */

export const tokens = ${JSON.stringify(tokenObject, null, 2)} as const;

// Type exports for TypeScript autocomplete
export type EntityType = keyof typeof tokens.color.entity;
export type QuestionType = keyof typeof tokens.color.question;
export type SemanticColor = keyof typeof tokens.color.semantic;
export type Spacing = keyof typeof tokens.space;
export type FontSize = keyof typeof tokens.font.size;
export type FontWeight = keyof typeof tokens.font.weight;
export type Duration = keyof typeof tokens.duration;
export type Easing = keyof typeof tokens.easing;
`;
  },
});

// Build configuration
const sd = new StyleDictionary({
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'dist/',
      files: [
        {
          destination: 'tokens.css',
          format: 'css/variables',
          options: {
            outputReferences: true,
          },
        },
      ],
    },
    scss: {
      transformGroup: 'scss',
      buildPath: 'dist/',
      files: [
        {
          destination: 'tokens.scss',
          format: 'scss/variables',
          options: {
            outputReferences: true,
          },
        },
      ],
    },
    js: {
      transformGroup: 'js',
      buildPath: 'dist/',
      files: [
        {
          destination: 'tokens.js',
          format: 'javascript/es6',
        },
        {
          destination: 'tokens.ts',
          format: 'typescript/es6-declarations',
        },
      ],
    },
  },
});

// Build all platforms
console.log('Building design tokens...');
await sd.buildAllPlatforms();
console.log('✓ Design tokens built successfully!');
