// Client-side cart with quantity controls, mini-cart, and persisted customer fields
const CART_KEY = 'kopernik_cart'
const CUSTOMER_STORAGE_KEY = 'kopernik_customer'

// Inject toast element
;(function(){
  const t = document.createElement('div'); t.id='__kopernik_toast'; t.className='toast'; document.body.appendChild(t)
  window.showToast = function(msg, ms=1600){ const el = document.getElementById('__kopernik_toast'); el.innerText = msg; el.classList.add('show'); setTimeout(()=>el.classList.remove('show'), ms) }
})();

// Do not pre-initialize window.PIZZAS here — build it from server data or from .card elements below

// debug marker (use console.log so it's visible by default)
try{ console.log('[order.js] loaded') }catch(e){}

function loadCart(){
  try{
    const raw = JSON.parse(localStorage.getItem(CART_KEY) || '[]')
    if(!Array.isArray(raw)) return []
    // normalize entries: support both old format (pizza_id) and new format (item_id, item_type)
    return raw.map(it=>{
      if(it.pizza_id && !it.item_id) {
        // Convert old format to new format
        return { item_id: Number(it.pizza_id), item_type: 'pizza', quantity: Number(it.quantity) }
      } else {
        return { item_id: Number(it.item_id), item_type: it.item_type || 'pizza', quantity: Number(it.quantity) }
      }
    }).filter(it=> Number.isFinite(it.item_id) && Number.isFinite(it.quantity) && it.quantity>0)
  }catch(e){ return [] }
}
function saveCart(c){ const s = JSON.stringify(c); localStorage.setItem(CART_KEY, s); }

function updateMiniCount(){
  const c = loadCart().reduce((s,i)=>s+i.quantity,0)
  const el = document.getElementById('mini-count')
  if(el) el.innerText = c
  try{ console.log('[order.js] updateMiniCount', c) }catch(e){}
}

function bindCartButtons(){
  // Keep explicit bindings for existing elements (useful for older browsers)
  document.querySelectorAll('.qty-incr').forEach(b=> b.onclick = ()=>{ changeQty(Number(b.dataset.pid), 1) })
  document.querySelectorAll('.qty-decr').forEach(b=> b.onclick = ()=>{ changeQty(Number(b.dataset.pid), -1) })
  document.querySelectorAll('.remove-item').forEach(b=> b.onclick = ()=>{ removeItem(Number(b.dataset.pid)) })
}

function getItemInfo(item_id, item_type) {
  // Helper function to get item info from various sources
  let items = []
  if (item_type === 'pizza' && window.PIZZAS) {
    items = window.PIZZAS
  } else if (item_type === 'drink' && window.DRINKS) {
    items = window.DRINKS
  } else if (item_type === 'dessert' && window.DESSERTS) {
    items = window.DESSERTS
  } else if (window.ALL_ITEMS) {
    items = window.ALL_ITEMS.filter(i => i.type === item_type)
  }
  
  return items.find(i => i.id == item_id) || null
}

function renderCart(){
  const cart = loadCart()
  // renderCart called
  const itemsDiv = document.getElementById('cart-items')
  // always update mini count and dropdown even when not on checkout page
  updateMiniCount()
  const miniDrop = document.getElementById('mini-dropdown')
  if(miniDrop){
    miniDrop.innerHTML = ''
    if(cart.length === 0){ miniDrop.innerHTML = '<div style="padding:8px">Cart is empty</div>' }
    cart.forEach(it=>{
      const itemInfo = getItemInfo(it.item_id, it.item_type)
      const name = itemInfo ? itemInfo.name : `${it.item_type} ${it.item_id}`
      const price = itemInfo ? parseFloat(itemInfo.price) : 0
      const emoji = it.item_type === 'pizza' ? '🍕' : it.item_type === 'drink' ? '🥤' : '🍰'
      const div = document.createElement('div')
      div.className = 'mini-item'
      div.innerHTML = `<span>${emoji} ${name} x${it.quantity}</span><strong>€${(price*it.quantity).toFixed(2)}</strong>`
      miniDrop.appendChild(div)
    })
    if(cart.length>0){ const btn = document.createElement('div'); btn.style.textAlign='center'; btn.style.paddingTop='6px'; btn.innerHTML = `<a href='/checkout' class='checkout-btn'>Go to checkout</a>`; miniDrop.appendChild(btn) }
  }
  if(!itemsDiv) return
  // Always populate the checkout cart area when present
  itemsDiv.innerHTML = ''
  if(cart.length === 0){
    itemsDiv.innerHTML = '<p>Your cart is empty.</p>'
    const ct = document.getElementById('cart-total'); if(ct) ct.innerText = ''
    return
  }
  let total = 0
  const frag = document.createDocumentFragment()
  cart.forEach(it=>{
    const itemInfo = getItemInfo(it.item_id, it.item_type)
    const name = itemInfo ? itemInfo.name : `${it.item_type} ${it.item_id}`
    const unit = itemInfo ? parseFloat(itemInfo.price) : 0
    const line = unit * it.quantity
    const emoji = it.item_type === 'pizza' ? '🍕' : it.item_type === 'drink' ? '🥤' : '🍰'
    const div = document.createElement('div')
    div.className = 'cart-line'
    div.innerHTML = `
      <strong>${emoji} ${name}</strong> — €${unit.toFixed(2)} ×
      <button class="qty-decr" data-item-id="${it.item_id}" data-item-type="${it.item_type}">-</button>
      <span class="qty">${it.quantity}</span>
      <button class="qty-incr" data-item-id="${it.item_id}" data-item-type="${it.item_type}">+</button>
      = €${line.toFixed(2)}
      <button class="remove-item" data-item-id="${it.item_id}" data-item-type="${it.item_type}">Remove</button>
    `
    frag.appendChild(div)
    total += line
  })
  itemsDiv.appendChild(frag)
  const ct = document.getElementById('cart-total'); if(ct) ct.innerText = 'Estimated total: €' + total.toFixed(2)
  bindCartButtons()
  try{ console.log('[order.js] rendered checkout HTML:', itemsDiv.innerHTML) }catch(e){}
}

function addToCart(item_id, item_type = 'pizza'){
  try{ console.log('[order.js] addToCart called id=', item_id, 'type=', item_type) }catch(e){}
  const cart = loadCart()
  const existing = cart.find(c=>c.item_id === item_id && c.item_type === item_type)
  if(existing) existing.quantity += 1
  else cart.push({item_id, item_type, quantity:1})
  saveCart(cart)
  renderCart()
  if(typeof window.showToast === 'function'){
    try{ window.showToast('Added to cart') }catch(e){ console.log('[order.js] showToast threw', e) }
  } else { console.log('[order.js] showToast not available') }
}

function changeQty(item_id, delta, item_type = 'pizza'){
  const cart = loadCart()
  const it = cart.find(c=>c.item_id===item_id && c.item_type===item_type)
  if(!it) return
  it.quantity += delta
  if(it.quantity <= 0){ const idx = cart.findIndex(c=>c.item_id===item_id && c.item_type===item_type); cart.splice(idx,1) }
  saveCart(cart)
  renderCart()
}

function removeItem(item_id, item_type = 'pizza'){
  const cart = loadCart().filter(c=>!(c.item_id===item_id && c.item_type===item_type))
  saveCart(cart)
  renderCart()
}

function initCart(){
  try{ console.log('[order.js] initCart start; PIZZAS keys=', Object.keys(window.PIZZAS||{}), 'storedCart=', localStorage.getItem(CART_KEY)) }catch(e){}
  // build a price/name map from server-rendered data OR from the .card elements on the page
  // If the server already provided window.PIZZAS (on /checkout), keep it. Otherwise, when .card elements exist (on /menu), build the map.
  if(document.querySelectorAll('.card').length > 0){
    const cards = document.querySelectorAll('.card')
    try{ console.log('[order.js] found .card elements:', cards.length) }catch(e){}
    window.PIZZAS = window.PIZZAS || {}
    cards.forEach(card=>{
      const pid = parseInt(card.dataset.pid)
      const price = Number(card.dataset.price)
      const name = card.dataset.name || null
      try{ console.log('[order.js] building PIZZAS entry for pid=', pid, 'name=', name, 'price=', price) }catch(e){}
      if(Number.isFinite(pid)) window.PIZZAS[pid] = { name: name || (`Pizza ${pid}`), price: Number.isFinite(price) ? price : 0 }
    })
  }

  // attach add-to-cart buttons using event delegation so clicks are handled
  // even if buttons are added/modified after init or binding fails due to timing
  try{ console.log('[order.js] setting delegated add-to-cart handler') }catch(e){}
  document.addEventListener('click', function(e){
    // support browsers that have closest on elements
    const btn = e.target && (e.target.closest ? e.target.closest('.add-to-cart') : (e.target.classList && e.target.classList.contains('add-to-cart') ? e.target : null))
    if(!btn) return
    e.preventDefault()
    // get item id and type from button dataset or from enclosing .card
    let itemAttr = null, typeAttr = null
    try{
      if(btn.dataset && btn.dataset.pid) {
        itemAttr = btn.dataset.pid
        typeAttr = btn.dataset.type
      } else if(btn.closest){ 
        const c = btn.closest('.card')
        if(c && c.dataset) {
          itemAttr = c.dataset.pid
          typeAttr = c.dataset.type
        }
      }
    }catch(e){ try{ console.warn('[order.js] item attr extraction error', e) }catch(_){} }
    
    // Extract item ID from formats like "pizza-1", "drink-2", "dessert-3"
    let itemId = null, itemType = 'pizza'
    if(itemAttr && itemAttr.includes('-')) {
      const parts = itemAttr.split('-')
      if(parts.length >= 2) {
        itemType = parts[0]
        itemId = parseInt(parts[1], 10)
      }
    } else {
      itemId = parseInt(itemAttr, 10)
    }
    
    // Override with explicit type if available
    if(typeAttr) itemType = typeAttr
    
    try{ console.log('[order.js] add-to-cart click detected', { itemAttr, itemId, itemType, btn }) }catch(e){}
    if(isNaN(itemId)){
      try{ console.warn('[order.js] add-to-cart clicked but item id missing or invalid', itemAttr) }catch(e){}
      return
    }
    try{
      addToCart(itemId, itemType)
    }catch(err){
      console.error('[order.js] addToCart threw', err)
    }
  })

  // also delegate quantity and remove button clicks (works after render)
  document.addEventListener('click', function(e){
    const incr = e.target && (e.target.closest ? e.target.closest('.qty-incr') : (e.target.classList && e.target.classList.contains('qty-incr') ? e.target : null))
    if(incr){ 
      e.preventDefault()
      const itemId = Number(incr.dataset.itemId || incr.dataset.pid)
      const itemType = incr.dataset.itemType || incr.dataset.type || 'pizza'
      if(!isNaN(itemId)) changeQty(itemId, 1, itemType)
      return 
    }
    const decr = e.target && (e.target.closest ? e.target.closest('.qty-decr') : (e.target.classList && e.target.classList.contains('qty-decr') ? e.target : null))
    if(decr){ 
      e.preventDefault()
      const itemId = Number(decr.dataset.itemId || decr.dataset.pid)
      const itemType = decr.dataset.itemType || decr.dataset.type || 'pizza'
      if(!isNaN(itemId)) changeQty(itemId, -1, itemType)
      return 
    }
    const rem = e.target && (e.target.closest ? e.target.closest('.remove-item') : (e.target.classList && e.target.classList.contains('remove-item') ? e.target : null))
    if(rem){ 
      e.preventDefault()
      const itemId = Number(rem.dataset.itemId || rem.dataset.pid)
      const itemType = rem.dataset.itemType || rem.dataset.type || 'pizza'
      if(!isNaN(itemId)) removeItem(itemId, itemType)
      return 
    }
  })

  // Note: we don't auto-navigate on mini-cart click here — the dropdown toggle is handled below.

  renderCart()

  // mini dropdown behavior
  const miniDrop = document.getElementById('mini-dropdown')
  function renderMini(){
    const cart = loadCart()
    if(!miniDrop) return
    miniDrop.innerHTML = ''
    if(cart.length === 0){ miniDrop.innerHTML = '<div style="padding:8px">Cart is empty</div>'; return }
    cart.forEach(it=>{
      const p = window.PIZZAS && window.PIZZAS[it.pizza_id]
      const name = p ? p.name : `Pizza ${it.pizza_id}`
      const div = document.createElement('div')
      div.className = 'mini-item'
      div.innerHTML = `<span>${name} x${it.quantity}</span><strong>€${((p?parseFloat(p.price):0)*it.quantity).toFixed(2)}</strong>`
      miniDrop.appendChild(div)
    })
    const btn = document.createElement('div')
    btn.style.textAlign = 'center'
    btn.style.paddingTop = '6px'
    btn.innerHTML = `<a href='/checkout' class='checkout-btn'>Go to checkout</a>`
    miniDrop.appendChild(btn)
  }
  renderMini()
  // toggle dropdown
  const miniBtn = document.getElementById('mini-cart')
  if(miniBtn && miniDrop) miniBtn.addEventListener('click', (e)=>{ e.stopPropagation(); miniDrop.classList.toggle('visible') })
  document.addEventListener('click', ()=>{ if(miniDrop) miniDrop.classList.remove('visible') })

  // order form handling and customer persistence
  const form = document.getElementById('order-form')
  if(form){
    // prefill
    try{ const saved = JSON.parse(localStorage.getItem(CUSTOMER_STORAGE_KEY) || '{}'); Object.keys(saved).forEach(k=>{ if(form[k]) form[k].value = saved[k] }) }catch(e){}
    ['name','email','phone','address','birthday','discount_code'].forEach(k=>{
      if(form[k]) form[k].addEventListener('input', ()=>{
        const obj = JSON.parse(localStorage.getItem(CUSTOMER_STORAGE_KEY) || '{}')
        obj[k]=form[k].value
        localStorage.setItem(CUSTOMER_STORAGE_KEY, JSON.stringify(obj))
      })
    })
    form.addEventListener('submit', async (e)=>{
      e.preventDefault()
      const cart = loadCart()
      if(cart.length === 0){ alert('Cart is empty'); return }
      const payload = {
        customer: {
          name: form.name.value,
          email: form.email.value,
          phone: form.phone.value,
          address: form.address.value,
          birthday: form.birthday.value || undefined
        },
        items: cart.map(i=>({
          item_id: i.item_id, 
          item_type: i.item_type, 
          quantity: i.quantity,
          // Include legacy format for backward compatibility
          pizza_id: i.item_type === 'pizza' ? i.item_id : undefined
        })),
        discount_code: form.discount_code.value || undefined
      }
      const res = await fetch('/orders', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)})
      const json = await res.json()
      const out = document.getElementById('order-result')
      if(res.status === 201){
        if (json.delivery_person && json.delivery_person.startsWith("No courier")) {
          out.innerText = `Order placed! id=${json.order_id}, total=${json.total} ⚠️ ${json.delivery_person}`;
        } else {
          out.innerText = `Order placed! id=${json.order_id}, total=${json.total}, delivery by ${json.delivery_person}`;
        }
      localStorage.removeItem(CART_KEY);
      renderCart();
      }
      else {
        out.innerText = 'Error: ' + (json.error || JSON.stringify(json));
      }
    })
  }
}

// initialize immediately if DOM already loaded, otherwise wait for DOMContentLoaded
if(document.readyState === 'loading') window.addEventListener('DOMContentLoaded', initCart)
else initCart()

// expose some helpers for debugging in the browser console
try{
  window.renderCart = renderCart
  window.addToCart = addToCart
  window.loadCart = loadCart
  window.saveCart = saveCart
  console.log('[order.js] helpers exposed on window: renderCart, addToCart, loadCart')
}catch(e){}
