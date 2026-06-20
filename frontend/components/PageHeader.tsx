export function PageHeader({eyebrow, title, description, action}: {eyebrow: string; title: string; description: string; action?: React.ReactNode}) {
  return (
    <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div><div className="eyebrow">{eyebrow}</div><h1 className="page-title mt-2">{title}</h1><p className="muted mt-2 max-w-2xl">{description}</p></div>
      {action}
    </div>
  );
}

