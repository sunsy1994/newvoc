export default function ImportTasksPage() {
  return <Placeholder title="导入任务" desc="上传事件、内容、评论ODS文件，并触发ETL作业。" />;
}

function Placeholder({ title, desc }: { title: string; desc: string }) {
  return (
    <section>
      <h1 className="text-2xl font-semibold text-zinc-950">{title}</h1>
      <p className="mt-2 text-sm text-zinc-500">{desc}</p>
    </section>
  );
}
