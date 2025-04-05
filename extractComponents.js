const fs = require('fs');
const path = require('path');

module.exports = function transformer(file, api) {
  const j = api.jscodeshift;
  const root = j(file.source);

  const outputDir = './extracted';
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

  const fileName = path.basename(file.path).replace(/\.[jt]sx?$/, '');

  root.find(j.FunctionDeclaration).forEach(path => {
    const name = path.value.id?.name || 'Unnamed';
    const code = j(path).toSource();
    fs.writeFileSync(`${outputDir}/${fileName}_${name}.js`, code, 'utf8');
  });

  root.find(j.VariableDeclarator)
    .filter(p =>
      p.value.init &&
      (j.ArrowFunctionExpression.check(p.value.init) || j.FunctionExpression.check(p.value.init))
    )
    .forEach(path => {
      const name = path.value.id.name;
      const code = j(path).toSource();
      fs.writeFileSync(`${outputDir}/${fileName}_${name}.js`, code, 'utf8');
    });

  return file.source;
};
