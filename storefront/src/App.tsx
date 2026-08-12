import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { RefObject } from "react";
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

function useDialogFocus(
  open: boolean,
  onClose: () => void,
  container: RefObject<HTMLElement | null>,
) {
  const restoreFocus = useRef<HTMLElement | null>(null);
  useEffect(() => {
    if (!open || !container.current) return;
    restoreFocus.current =
      document.activeElement instanceof HTMLElement
        ? document.activeElement
        : null;
    const root = container.current;
    const focusable = () =>
      Array.from(
        root.querySelectorAll<HTMLElement>(
          'a[href],button:not([disabled]),textarea,input,select,[tabindex]:not([tabindex="-1"])',
        ),
      );
    const timer = window.setTimeout(() => focusable()[0]?.focus(), 0);
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;
      const controls = focusable();
      if (!controls.length) return;
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => {
      window.clearTimeout(timer);
      document.removeEventListener("keydown", handleKey);
      restoreFocus.current?.focus();
    };
  }, [container, onClose, open]);
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
        <span className="product-card__meta">
          <span>{product.category}</span>
          <span>{product.model}</span>
        </span>
        <strong>{product.name}</strong>
        <span className="product-card__foot">
          <span>{money(product.price)}</span>
          <span className="text-action">
            Configure <ArrowRight aria-hidden />
          </span>
        </span>
      </button>
    </article>
  );
}

function RequestDrawer({
  items,
  onClose,
  onRemove,
  onClear,
}: {
  items: RequestItem[];
  onClose: () => void;
  onRemove: (key: string) => void;
  onClear: () => void;
}) {
  const [sent, setSent] = useState(false);
  const drawerRef = useRef<HTMLElement>(null);
  useDialogFocus(true, onClose, drawerRef);
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
    <aside
      className="drawer is-open"
      role="dialog"
      aria-modal="true"
      aria-labelledby="request-title"
      ref={drawerRef}
    >
      <div className="drawer__head">
        <div>
          <span className="section-label">Order request</span>
          <h2 id="request-title">
            Request list <b>{items.length}</b>
          </h2>
        </div>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close request list"
        >
          <X />
        </button>
      </div>
      <p className="boundary">
        <ClipboardText /> Request preview. No payment is processed.
      </p>
      <p className="drawer-notice">{NOTICE}</p>
      {items.length === 0 ? (
        <div className="empty-state">
          <ShoppingBagOpen />
          <h3>Your request is empty</h3>
          <p>
            Configure a product to keep its fit and option details together.
          </p>
        </div>
      ) : (
        <>
          <div className="request-items">
            {items.map((item) => (
              <article className="request-item" key={item.key}>
                <img src={item.product.image} alt="" />
                <div>
                  <strong>{item.product.name}</strong>
                  <span>
                    {item.product.model} · Qty {item.quantity}
                  </span>
                  <small>{Object.values(item.selections).join(" · ")}</small>
                  {item.note && (
                    <small className="request-note">
                      <b>Notes:</b> {item.note}
                    </small>
                  )}
                </div>
                <button
                  className="icon-button small"
                  onClick={() => onRemove(item.key)}
                  aria-label={`Remove ${item.product.name}`}
                >
                  <Trash />
                </button>
              </article>
            ))}
          </div>
          <div className="drawer__actions">
            <a
              className="button primary full"
              href={href}
              onClick={() => setSent(true)}
            >
              <EnvelopeSimple /> Draft email request <ArrowRight />
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
    </aside>
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
  const [drawer, setDrawer] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [sizeGuide, setSizeGuide] = useState(false);
  const sizeDialogRef = useRef<HTMLElement>(null);
  const closeDrawer = useCallback(() => setDrawer(false), []);
  const closeSizeGuide = useCallback(() => setSizeGuide(false), []);
  useDialogFocus(sizeGuide, closeSizeGuide, sizeDialogRef);

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
    if (!isComplete) return;
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
            M&amp;T UNIFORMS<small>Professional outfitters</small>
          </span>
        </a>
        <label className="header-search">
          <MagnifyingGlass />
          <span className="sr-only">Search products</span>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search product, category, or model"
          />
        </label>
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
          <ClipboardText /> Request list <b>{items.length}</b>
        </button>
      </header>

      <main id="top">
        <section className="intro" aria-labelledby="intro-title">
          <div>
            <h1 id="intro-title">
              Find the right uniform.
              <br />
              Get the fit right.
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
                <span className="section-label">Recovered public catalog</span>
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
                <h3>No products match those filters</h3>
                <p>
                  Try a broader search, clear the filters, or ask the team
                  directly.
                </p>
                <div className="no-results-actions">
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
              <img src={selected.image} alt={selected.name} />
              <span className="source-stamp">Public snapshot</span>
            </div>
            <div className="configurator__body">
              <span className="section-label">
                {selected.brand} · {selected.model}
              </span>
              <h2>{selected.name}</h2>
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
              <div className="options">
                {selected.options.map((option) => (
                  <fieldset
                    key={option.id}
                    aria-invalid={option.required && !selections[option.id]}
                    aria-describedby={
                      option.required && !selections[option.id]
                        ? `${option.id}-help`
                        : undefined
                    }
                  >
                    <legend>
                      {option.label} {option.required && <span>Required</span>}
                    </legend>
                    <div className="choice-grid">
                      {option.values.map((value) => (
                        <button
                          type="button"
                          key={value}
                          className={
                            selections[option.id] === value ? "is-selected" : ""
                          }
                          aria-pressed={selections[option.id] === value}
                          onClick={() =>
                            setSelections((current) => ({
                              ...current,
                              [option.id]: value,
                            }))
                          }
                        >
                          {selections[option.id] === value && <Check />}
                          {value}
                        </button>
                      ))}
                    </div>
                    {option.required && !selections[option.id] && (
                      <small className="field-help" id={`${option.id}-help`}>
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
                disabled={!isComplete}
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
            <h2>Ordering still works while the new site is being built.</h2>
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
        <span>M.T. Uniforms · 525 Franklin St, Johnstown, PA 15901</span>
        <span>Prototype built from recovered public evidence</span>
      </footer>
      {drawer && (
        <>
          <RequestDrawer
            items={items}
            onClose={closeDrawer}
            onRemove={(key) =>
              setItems((current) => current.filter((item) => item.key !== key))
            }
            onClear={() => setItems([])}
          />
          <button
            className="scrim"
            onClick={closeDrawer}
            aria-label="Close request list overlay"
          />
        </>
      )}
      {sizeGuide && (
        <div className="modal-wrap" role="presentation">
          <button
            className="scrim"
            onClick={closeSizeGuide}
            aria-label="Close size guide"
          />
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="size-title"
            ref={sizeDialogRef}
          >
            <div className="drawer__head">
              <div>
                <span className="section-label">Fit guidance</span>
                <h2 id="size-title">Confirm before you order</h2>
              </div>
              <button
                className="icon-button"
                onClick={closeSizeGuide}
                aria-label="Close size guide"
              >
                <X />
              </button>
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
          </section>
        </div>
      )}
    </div>
  );
}
