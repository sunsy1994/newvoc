import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import ts from 'typescript';

function loadStrategyModule() {
  const filePath = join(process.cwd(), 'src/components/assets/eventVocStrategy.ts');
  const source = readFileSync(filePath, 'utf8');
  const transpiled = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
  }).outputText;

  const module = { exports: {} };
  const fn = new Function('module', 'exports', transpiled);
  fn(module, module.exports);
  return module.exports;
}

const strategy = loadStrategyModule();

assert.equal(strategy.classifyEventScenario('新品上市'), '营销事件');
assert.equal(strategy.classifyEventScenario('品牌传播'), '营销事件');
assert.equal(strategy.classifyEventScenario('质量争议'), '产品舆情事件');
assert.equal(strategy.classifyEventScenario('服务体验'), '产品舆情事件');

const marketingFocus = strategy.getEventStoryFocus('新品上市');
assert.equal(marketingFocus.coreQuestion, '这次传播有没有打到目标人群？');
assert.ok(marketingFocus.analysisPath.includes('主命题与用户记忆点'));

const productRiskFocus = strategy.getEventStoryFocus('质量争议');
assert.equal(productRiskFocus.coreQuestion, '这个问题是真风险，还是局部噪音？');
assert.ok(productRiskFocus.analysisPath.includes('证据强度与车相关样本'));

const marketingMetrics = strategy.getEventMetricSet('品牌传播');
assert.ok(marketingMetrics.primaryMetrics.includes('主命题Top'));
assert.ok(marketingMetrics.primaryMetrics.includes('有效互动率'));
assert.ok(!marketingMetrics.primaryMetrics.includes('投放ROI'));

const riskMetrics = strategy.getEventMetricSet('质量争议');
assert.ok(riskMetrics.primaryMetrics.includes('证据强度'));
assert.ok(!riskMetrics.primaryMetrics.includes('问题集中度'));
assert.ok(!riskMetrics.primaryMetrics.includes('高置信样本数'));
assert.ok(!riskMetrics.primaryMetrics.includes('风险等级'));

const departmentStories = strategy.getSupportedDepartmentStories();
assert.deepEqual(
  departmentStories.map((item) => item.department),
  ['市场部', '产品部', '销售部', '售后部', '公关部']
);
assert.ok(departmentStories.find((item) => item.department === '销售部').stories.includes('价格感知'));
assert.ok(departmentStories.find((item) => item.department === '售后部').deferred.includes('服务网络差异'));
assert.ok(!departmentStories.find((item) => item.department === '产品部').requiredData.includes('高置信评论'));
assert.ok(strategy.getEffectiveEngagementDefinition().includes('探讨与车相关'));

const readiness = strategy.getDataReadinessChecklist();
assert.deepEqual(
  readiness.map((group) => group.priority),
  ['P0', 'P1', 'P2']
);
assert.ok(readiness[0].items.includes('事件表'));
assert.ok(readiness[1].items.includes('KOL受众心智分布'));

const summary = strategy.getEventStrategySummary('新品上市', 'S9');
assert.match(summary, /S9/);
assert.match(summary, /精准投放/);

console.log('eventVocStrategy tests passed');
