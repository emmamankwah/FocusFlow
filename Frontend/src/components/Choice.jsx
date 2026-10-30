// Radio group drawn as selectable tiles. Works with react-hook-form's register.
export default function Choice({ legend, name, options, register, columns = 3 }) {
  return (
    <fieldset>
      <legend className="mb-1.5 text-[0.85rem] font-semibold text-inkwell">{legend}</legend>
      <div className={`grid gap-2 ${columns === 3 ? 'grid-cols-3' : 'grid-cols-2'}`}>
        {options.map((option) => (
          <label key={option.value} className="cursor-pointer">
            <input type="radio" value={option.value} className="peer sr-only" {...register(name)} />
            <span className="block rounded-xl border border-inkwell/15 bg-white px-2.5 py-2.5 text-center transition-colors hover:border-inkwell/40 peer-checked:border-cobalt peer-checked:bg-cobalt/5 peer-checked:ring-2 peer-checked:ring-cobalt/25 peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-cobalt">
              <span className="block text-[0.8rem] font-semibold text-inkwell">{option.label}</span>
              {option.hint && (
                <span className="mt-0.5 block text-[0.64rem] text-inkwell/55">{option.hint}</span>
              )}
            </span>
          </label>
        ))}
      </div>
    </fieldset>
  )
}
