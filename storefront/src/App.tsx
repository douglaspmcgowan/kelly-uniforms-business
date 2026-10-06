import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Dialog } from "@base-ui/react/dialog";
import { Toggle } from "@base-ui/react/toggle";
import { ToggleGroup } from "@base-ui/react/toggle-group";
import {
  ArrowRight,
  Buildings,
  Check,
  ClipboardText,
  EnvelopeSimple,
  Fire,
  Headset,
  List,
  MagnifyingGlass,
  Minus,
  Package,
  Phone,
  Plus,
  Shield,
  ShoppingBagOpen,
  SlidersHorizontal,
  Trash,
  Truck,
  UserFocus,
  X,
} from "@phosphor-icons/react";
import {
  CATEGORIES,
  EMAIL,
  NOTICE,
  PHONE,
  PRODUCTS,
  Product,
  ROLES,
} from "./data";

type Selections = Record<string, string>;
type RequestItem = {
  key: string;
  product: Product;
  selections: Selections;
  quantity: number;
  note: string;
};

const roleIcons = [Shield, Fire, UserFocus, Buildings, Shield, Package];

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

const FIT_OPTION_IDS = ["size", "waist", "inseam"];

function SizeChart({ product }: { product: Product }) {
  const fit = product.options.filter((option) =>
    FIT_OPTION_IDS.includes(option.id),
  );
  const rows = Math.max(0, ...fit.map((option) => option.values.length));
  return (
    <section className="size-chart" aria-labelledby="size-chart-title">
      <h3 id="size-chart-title">Size chart</h3>
      {fit.length ? (
        <table>
          <caption className="sr-only">
            Sizes listed in the public snapshot for {product.name}
          </caption>
          <thead>
            <tr>
              {fit.map((option) => (
                <th scope="col" key={option.id}>
                  {option.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: rows }, (_, index) => (
              <tr key={index}>
                {fit.map((option) => (
                  <td key={option.id}>{option.values[index] ?? ""}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>This item lists no sizes in the public snapshot.</p>
      )}
      <p className="size-chart__note">
        Measurements on file with the shop; call{" "}
        <a href="tel:+18145362390">{PHONE}</a>
      </p>
    </section>
  );
}

function ProductCard({
  product,
  active,
  onSelect,
}: {
  product: Product;
  active: boolean;
  onSelect: () => void;
}) {
  return (
    <article className={`product-card ${active ? "is-active" : ""}`}>
      <button
        className="product-card__hit"
        onClick={onSelect}
        aria-label={`Configure ${product.name}`}
      >
        <span className="product-card__media">
          <img src={product.image} alt={product.name} />
        </span>
        <span className="product-card__body">
          <strong className="product-card__title">{product.name}</strong>
          <span className="product-card__category">{product.category}</span>
          <span className="product-card__row">
            <span>{product.model}</span>
            <span className="product-card__price">{money(product.price)}</span>
          </span>
          <span className="text-action">
            Configure <ArrowRight aria-hidden />
          </span>
        </span>
      </button>
    </article>
  );
}

function RequestDrawer({
  open,
  items,
  onClose,
  onRemove,
  onClear,
  onBrowse,
  finalFocus,
}: {
  open: boolean;
  items: RequestItem[];
  onClose: () => void;
  onRemove: (key: string) => void;
  onClear: () => void;
  onBrowse: () => void;
  finalFocus: () => boolean | HTMLElement | null | void;
}) {
  return (
    <Dialog.Root
      open={open}
      onOpenChange={(next) => {
        if (!next) onClose();
      }}
    >
      <Dialog.Portal>
        <Dialog.Backdrop className="scrim" />
        <Dialog.Popup className="drawer" finalFocus={finalFocus}>
          <DrawerBody
            items={items}
            onRemove={onRemove}
            onClear={onClear}
            onBrowse={onBrowse}
          />
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  );
}

function DrawerBody({
  items,
  onRemove,
  onClear,
  onBrowse,
}: {
  items: RequestItem[];
  onRemove: (key: string) => void;
  onClear: () => void;
  onBrowse: () => void;
}) {
  const [sent, setSent] = useState(false);
  const draft = useMemo(() => {
    const lines = items.flatMap((item, index) => [
      `${index + 1}. ${item.product.name} (${item.product.model})`,
      `   ${Object.entries(item.selections)
        .map(([k, v]) => `${k}: ${v}`)
        .join(", ")}`,
      `   Quantity: ${item.quantity}${item.note ? `, Notes: ${item.note}` : ""}`,
    ]);
    return `Hello M.T. Uniforms,\n\nPlease help me confirm this order request:\n\n${lines.join("\n")}\n\nPreferred fulfillment: please confirm with me.\n\nThank you.`;
  }, [items]);
  const href = `mailto:${EMAIL}?subject=${encodeURIComponent("M.T. Uniforms order request")}&body=${encodeURIComponent(draft)}`;
  return (
    <>
      <div className="drawer__head">
        <div>
          <Dialog.Title id="request-title">
            Request list <b>{items.length}</b>
          </Dialog.Title>
        </div>
        <Dialog.Close className="icon-button" aria-label="Close request list">
          <X />
        </Dialog.Close>
      </div>
      <p className="boundary">
        <ClipboardText /> Request preview. No payment is processed.
      </p>
      <p className="drawer-notice">{NOTICE}</p>
      {items.length === 0 ? (
        <div className="empty-state">
          <ShoppingBagOpen />
          <h3>Your request is empty</h3>
          <p>Configure a garment and add it to build the order sheet.</p>
          <button className="button secondary" onClick={onBrowse}>
            Browse the catalogue
          </button>
        </div>
      ) : (
        <>
          <section className="order-sheet" aria-labelledby="order-sheet-title">
            <h3 id="order-sheet-title">Order sheet</h3>
            <p className="order-sheet__note">
              One row per garment. Put the department name in the notes so the
              shop can group the order.
            </p>
            <div className="order-sheet__scroll">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Garment</th>
                    <th scope="col">Size and options</th>
                    <th scope="col" className="num">
                      Qty
                    </th>
                    <th scope="col">Notes</th>
                    <th scope="col">
                      <span className="sr-only">Remove</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((item) => (
                    <tr key={item.key}>
                      <td data-label="Garment">
                        <span className="order-garment">
                          <img src={item.product.image} alt="" />
                          <span>
                            <strong>{item.product.name}</strong>
                            <small>
                              {item.product.model},{" "}
                              <span className="num">
                                {money(item.product.price)}
                              </span>
                            </small>
                          </span>
                        </span>
                      </td>
                      <td data-label="Size and options">
                        {Object.values(item.selections).join(", ")}
                      </td>
                      <td data-label="Qty" className="num">
                        {item.quantity}
                      </td>
                      <td data-label="Notes" className="request-note">
                        {item.note || "No notes"}
                      </td>
                      <td className="order-remove">
                        <button
                          className="icon-button small"
                          onClick={() => onRemove(item.key)}
                          aria-label={`Remove ${item.product.name}`}
                        >
                          <Trash />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <div className="drawer__actions">
            <a
              className="button secondary full"
              href={href}
              onClick={() => setSent(true)}
            >
              <EnvelopeSimple /> Draft email request
            </a>
            <a className="button secondary full" href="tel:+18145362390">
              <Phone /> Call {PHONE}
            </a>
            <button className="text-button" onClick={onClear}>
              Clear request
            </button>
            {sent && (
              <p className="success" role="status">
                <Check /> Email draft opened. Review every detail before
                sending.
              </p>
            )}
          </div>
        </>
      )}
    </>
  );
}

export function App() {
  const [query, setQuery] = useState("");
  const [role, setRole] = useState("All roles");
  const [category, setCategory] = useState("All");
  const [selected, setSelected] = useState<Product>(PRODUCTS[0]);
  const [selections, setSelections] = useState<Selections>({});
  const [quantity, setQuantity] = useState(1);
  const [note, setNote] = useState("");
  const [fulfillment, setFulfillment] = useState("Pickup");
  const [items, setItems] = useState<RequestItem[]>([]);
  // Motion (d) hook: the header badge pulses once when the count grows.
  const prevCount = useRef(0);
  const countGrew = items.length > prevCount.current;
  useEffect(() => {
    prevCount.current = items.length;
  }, [items.length]);
  const [drawer, setDrawer] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [sizeGuide, setSizeGuide] = useState(false);
  const [attempted, setAttempted] = useState(false);
  const optionsRef = useRef<HTMLDivElement>(null);
  const browseRef = useRef(false);
  const closeDrawer = useCallback(() => setDrawer(false), []);
  const browseCatalogue = useCallback(() => {
    browseRef.current = true;
    setDrawer(false);
    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    document
      .getElementById("catalog")
      ?.scrollIntoView({
        behavior: reducedMotion ? "auto" : "smooth",
        block: "start",
      });
  }, []);
  // After the drawer closes, focus returns to the control that opened it,
  // unless the shopper asked to browse: then it lands on the first plate.
  const drawerFinalFocus = useCallback(() => {
    if (!browseRef.current) return true;
    browseRef.current = false;
    return document.querySelector<HTMLElement>(".product-card__hit") ?? true;
  }, []);

  const filtered = useMemo(
    () =>
      PRODUCTS.filter((product) => {
        const haystack =
          `${product.name} ${product.brand} ${product.model} ${product.category}`.toLowerCase();
        return (
          (!query || haystack.includes(query.toLowerCase())) &&
          (role === "All roles" || product.roles.includes(role)) &&
          (category === "All" || product.category === category)
        );
      }),
    [query, role, category],
  );

  const selectProduct = (product: Product) => {
    setSelected(product);
    setSelections({});
    setQuantity(1);
    setNote("");
    setAttempted(false);
    const reducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)",
    ).matches;
    document
      .getElementById("configure")
      ?.scrollIntoView({
        behavior: reducedMotion ? "auto" : "smooth",
        block: "start",
      });
  };

  const missingOptions = selected.options.filter(
    (option) => option.required && !selections[option.id],
  );
  const isComplete = missingOptions.length === 0;
  const addRequest = () => {
    if (!isComplete) {
      // The button stays enabled; the reason arrives on submit and focus moves to it.
      setAttempted(true);
      window.setTimeout(() => {
        optionsRef.current
          ?.querySelector<HTMLElement>('fieldset[aria-invalid="true"] button')
          ?.focus();
      }, 0);
      return;
    }
    setItems((current) => [
      ...current,
      {
        key: `${selected.id}-${Date.now()}`,
        product: selected,
        selections: { ...selections, Fulfillment: fulfillment },
        quantity,
        note,
      },
    ]);
    setDrawer(true);
  };

  const resetFilters = () => {
    setQuery("");
    setRole("All roles");
    setCategory("All");
  };

  return (
    <div className="app-shell">
      <a className="skip-link" href="#catalog">
        Skip to products
      </a>
      <div className="notice">
        {NOTICE}{" "}
        <span>
          <a href={`mailto:${EMAIL}`}>Email orders</a>
          <a href="tel:+18145362390">Call now</a>
        </span>
      </div>
      <header className="site-header">
        <a className="brand" href="#top" aria-label="M.T. Uniforms home">
          <span className="brand-mark">
            M<span>T</span>
          </span>
          <span>
            M.T. Uniforms<small>Professional outfitters</small>
          </span>
        </a>
        <nav
          className={mobileNav ? "is-open" : ""}
          aria-label="Main navigation"
        >
          <a href="#catalog">Shop</a>
          <a href="#help">Help</a>
          <a href={`mailto:${EMAIL}`}>Contact</a>
        </nav>
        <button
          className="icon-button mobile-menu"
          onClick={() => setMobileNav(!mobileNav)}
          aria-expanded={mobileNav}
          aria-label="Toggle navigation"
        >
          {mobileNav ? <X /> : <List />}
        </button>
        <button className="request-button" onClick={() => setDrawer(true)}>
          <ClipboardText /> <span className="request-label">Request list</span> <b key={items.length} data-pulse={countGrew ? "" : undefined}>
            {items.length}
          </b>
        </button>
      </header>

      <main id="top">
        <section className="intro" aria-labelledby="intro-title">
          <div>
            <h1 id="intro-title">
              Find the right uniform
              <br />
              Get the fit right
            </h1>
            <p>
              Browse the recovered public catalog, capture every option, then
              send the team one clear request.
            </p>
          </div>
          <div className="snapshot-note">
            <SlidersHorizontal />
            <span>
              <strong>Public catalog preview</strong>Prices and details reflect
              a recovered public snapshot. M.T. Uniforms will confirm every
              request.
            </span>
          </div>
        </section>

        <section className="workbench" id="catalog">
          <aside className="role-rail" aria-label="Filter by role">
            <div className="rail-heading">
              <span>Shop by role</span>
              <button className="text-button" onClick={resetFilters}>
                Reset
              </button>
            </div>
            <button
              className={role === "All roles" ? "is-active" : ""}
              onClick={() => setRole("All roles")}
            >
              <UserFocus />
              <span>All roles</span>
              {role === "All roles" && <Check />}
            </button>
            {ROLES.map((item, index) => {
              const Icon = roleIcons[index];
              return (
                <button
                  key={item}
                  className={role === item ? "is-active" : ""}
                  onClick={() => setRole(item)}
                >
                  <Icon />
                  <span>{item}</span>
                  {role === item && <Check />}
                </button>
              );
            })}
            <div className="rail-help" id="help">
              <Headset />
              <strong>Need a human?</strong>
              <p>Call or email with your department specifications.</p>
              <a href="tel:+18145362390">{PHONE}</a>
            </div>
          </aside>

          <div className="catalog-pane">
            <div className="catalog-search">
              <label htmlFor="catalog-search-input">Search products</label>
              <div className="catalog-search__field">
                <MagnifyingGlass aria-hidden />
                <input
                  id="catalog-search-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Product, category, or model"
                />
              </div>
            </div>
            <div className="category-tabs" aria-label="Filter by category">
              {CATEGORIES.map((item) => (
                <button
                  key={item}
                  className={category === item ? "is-active" : ""}
                  onClick={() => setCategory(item)}
                >
                  {item}
                </button>
              ))}
            </div>
            <div className="catalog-heading">
              <div>
                <h2>
                  {role === "All roles" ? "Uniforms and equipment" : role}
                </h2>
              </div>
              <span>
                {filtered.length} {filtered.length === 1 ? "item" : "items"}
              </span>
            </div>
            {filtered.length ? (
              <div className="product-grid">
                {filtered.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    active={selected.id === product.id}
                    onSelect={() => selectProduct(product)}
                  />
                ))}
              </div>
            ) : (
              <div className="empty-state catalog-empty">
                <MagnifyingGlass />
                <h3>
                  {query
                    ? `No products match \u201c${query}\u201d`
                    : "No products match those filters"}
                </h3>
                <p>
                  Try a broader search, clear the filters, or ask the team
                  directly.
                </p>
                <div className="no-results-actions">
                  {query && (
                    <button
                      className="button secondary"
                      onClick={() => setQuery("")}
                    >
                      Clear search
                    </button>
                  )}
                  <button className="button secondary" onClick={resetFilters}>
                    Clear filters
                  </button>
                  <a className="button secondary" href={`mailto:${EMAIL}`}>
                    Email orders
                  </a>
                  <a className="button secondary" href="tel:+18145362390">
                    Call now
                  </a>
                </div>
              </div>
            )}
          </div>

          <aside
            className="configurator"
            id="configure"
            aria-label="Configure selected product"
          >
            <div className="configurator__top">
              <div className="configurator__figure">
                <div className="configurator__image">
                  <img src={selected.image} alt={selected.name} />
                  <span className="source-stamp">Public snapshot</span>
                </div>
                <SizeChart product={selected} />
              </div>
            </div>
            <div className="configurator__body">
              <h2>{selected.name}</h2>
              <p className="product-meta">
                {selected.brand}, {selected.model}
              </p>
              <p>{selected.description}</p>
              <div className="price-line">
                <strong>{money(selected.price)}</strong>
                <a href={selected.sourceUrl} target="_blank" rel="noreferrer">
                  View source
                </a>
              </div>
              <button
                className="fit-callout"
                onClick={() => setSizeGuide(true)}
              >
                <span>
                  <strong>Fit guidance</strong>
                  {selected.fit}
                </span>
                <ArrowRight />
              </button>
              <div className="options" ref={optionsRef}>
                {selected.options.map((option) => (
                  <fieldset
                    key={option.id}
                    aria-invalid={
                      attempted && option.required && !selections[option.id]
                    }
                    aria-describedby={
                      attempted && option.required && !selections[option.id]
                        ? `${option.id}-help`
                        : undefined
                    }
                  >
                    <legend>
                      {option.label} {option.required && <span>Required</span>}
                    </legend>
                    <ToggleGroup
                      className="choice-grid"
                      aria-label={option.label}
                      value={
                        selections[option.id] ? [selections[option.id]] : []
                      }
                      onValueChange={(next) => {
                        // Single selection that stays chosen: pressing the
                        // chosen value again leaves it selected.
                        const chosen = next[0];
                        if (chosen)
                          setSelections((current) => ({
                            ...current,
                            [option.id]: chosen,
                          }));
                      }}
                    >
                      {option.values.map((value) => (
                        <Toggle key={value} value={value} className="choice">
                          {selections[option.id] === value && (
                            <Check weight="bold" aria-hidden />
                          )}
                          {value}
                        </Toggle>
                      ))}
                    </ToggleGroup>
                    {attempted && option.required && !selections[option.id] && (
                      <small
                        className="field-help"
                        id={`${option.id}-help`}
                        role="alert"
                      >
                        Choose a {option.label.toLowerCase()} to continue.
                      </small>
                    )}
                  </fieldset>
                ))}
              </div>
              <label className="notes-field">
                <span>
                  Personalization or order notes <small>Optional</small>
                </span>
                <textarea
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  maxLength={180}
                  placeholder="Name, patch placement, department standard, or questions"
                />
                <small>{note.length}/180</small>
              </label>
              <fieldset className="fulfillment">
                <legend>Fulfillment preference</legend>
                {["Ship", "Pickup", "Local delivery"].map((value) => (
                  <label key={value}>
                    <input
                      type="radio"
                      name="fulfillment"
                      value={value}
                      checked={fulfillment === value}
                      onChange={() => setFulfillment(value)}
                    />
                    {value === "Ship" ? (
                      <Truck />
                    ) : value === "Pickup" ? (
                      <Package />
                    ) : (
                      <Buildings />
                    )}
                    {value}
                  </label>
                ))}
              </fieldset>
              <div className="quantity-row">
                <span>Quantity</span>
                <div>
                  <button
                    onClick={() => setQuantity(Math.max(1, quantity - 1))}
                    aria-label="Decrease quantity"
                  >
                    <Minus />
                  </button>
                  <output>{quantity}</output>
                  <button
                    onClick={() => setQuantity(quantity + 1)}
                    aria-label="Increase quantity"
                  >
                    <Plus />
                  </button>
                </div>
              </div>
              <button
                className="button primary full"
                onClick={addRequest}
              >
                Add to request <ClipboardText />
              </button>
              <p className="payment-note">
                Request preview only. No payment is processed.
              </p>
            </div>
          </aside>
        </section>

        <section className="service-band">
          <div>
            <h2>Ordering still works while the new site is being built</h2>
            <p>
              Send the request list by email, or call the Johnstown team to
              confirm fit, customization, and fulfillment.
            </p>
          </div>
          <div>
            <a className="button primary" href={`mailto:${EMAIL}`}>
              <EnvelopeSimple /> {EMAIL}
            </a>
            <a className="button secondary" href="tel:+18145362390">
              <Phone /> {PHONE}
            </a>
          </div>
        </section>
      </main>

      <footer>
        <span>M.T. Uniforms, 525 Franklin St, Johnstown, PA 15901</span>
        <span>Prototype built from recovered public evidence</span>
      </footer>
      <RequestDrawer
        open={drawer}
        items={items}
        onClose={closeDrawer}
        onRemove={(key) =>
          setItems((current) => current.filter((item) => item.key !== key))
        }
        onClear={() => setItems([])}
        onBrowse={browseCatalogue}
        finalFocus={drawerFinalFocus}
      />
      <Dialog.Root open={sizeGuide} onOpenChange={setSizeGuide}>
        <Dialog.Portal>
          <Dialog.Backdrop className="scrim" />
          <Dialog.Popup className="modal">
            <div className="drawer__head">
              <div>
                <Dialog.Title id="size-title">
                  Confirm before you order
                </Dialog.Title>
              </div>
              <Dialog.Close
                className="icon-button"
                aria-label="Close size guide"
              >
                <X />
              </Dialog.Close>
            </div>
            <p>{selected.fit}</p>
            <ol>
              <li>
                Use the named option fields as the request starting point.
              </li>
              <li>Add department standards or alteration notes to the item.</li>
              <li>
                M.T. Uniforms confirms the final fit and availability with you.
              </li>
            </ol>
            <a className="button primary full" href="tel:+18145362390">
              <Phone /> Call for fit help
            </a>
          </Dialog.Popup>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  );
}
