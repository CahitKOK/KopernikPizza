// Client-side cart with quantity controls, mini-cart, and persisted customer fields
const CART_KEY = 'kopernik_cart'
const CUST_KEY = 'kopernik_cust'

// Inject toast element
(function(){
  const t = document.createElement('div'); t.id='__kopernik_toast'; t.className='toast'; document.body.appendChild(t)
  window.showToast = function(msg, ms=1600){ const el = document.getElementById('__kopernik_toast'); el.innerText = msg; el.classList.add('show'); setTimeout(()=>el.classList.remove('show'), ms) }
})()

// Do not pre-initialize window.PIZZAS here — build it from server data or from .card elements below

// debug marker (use console.log so it's visible by default)
try{ console.log('[order.js] loaded') }catch(e){}

function loadCart(){
  try{ return JSON.parse(localStorage.getItem(CART_KEY) || '[]') }catch(e){ return [] }
}
function saveCart(c){ const s = JSON.stringify(c); localStorage.setItem(CART_KEY, s); }

function updateMiniCount(){
  const c = loadCart().reduce((s,i)=>s+i.quantity,0)
  const el = document.getElementById('mini-count')
  if(el) el.innerText = c
  try{ console.log('[order.js] updateMiniCount', c) }catch(e){}
}

function bindCartButtons(){
  document.querySelectorAll('.qty-incr').forEach(b=> b.onclick = ()=>{ changeQty(parseInt(b.dataset.pid), 1) })
  document.querySelectorAll('.qty-decr').forEach(b=> b.onclick = ()=>{ changeQty(parseInt(b.dataset.pid), -1) })
  document.querySelectorAll('.remove-item').forEach(b=> b.onclick = ()=>{ removeItem(parseInt(b.dataset.pid)) })
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
      const p = window.PIZZAS && window.PIZZAS[it.pizza_id]
      const name = p ? p.name : `Pizza ${it.pizza_id}`
      const div = document.createElement('div')
      div.className = 'mini-item'
      div.innerHTML = `<span>${name} x${it.quantity}</span><strong>€${((p?parseFloat(p.price):0)*it.quantity).toFixed(2)}</strong>`
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
    const pinfo = (window.PIZZAS && window.PIZZAS[it.pizza_id]) || null
    const name = pinfo ? pinfo.name : `Pizza ${it.pizza_id}`
    const unit = pinfo ? parseFloat(pinfo.price) : 0
    const line = unit * it.quantity
    const div = document.createElement('div')
    div.className = 'cart-line'
    div.innerHTML = `
      <strong>${name}</strong> — €${unit.toFixed(2)} ×
      <button class="qty-decr" data-pid="${it.pizza_id}">-</button>
      <span class="qty">${it.quantity}</span>
      <button class="qty-incr" data-pid="${it.pizza_id}">+</button>
      = €${line.toFixed(2)}
      <button class="remove-item" data-pid="${it.pizza_id}">Remove</button>
    `
    frag.appendChild(div)
    total += line
  })
  itemsDiv.appendChild(frag)
  const ct = document.getElementById('cart-total'); if(ct) ct.innerText = 'Estimated total: €' + total.toFixed(2)
  bindCartButtons()
  try{ console.log('[order.js] rendered checkout HTML:', itemsDiv.innerHTML) }catch(e){}
}

function addToCart(pizza_id){
  try{ console.log('[order.js] addToCart called pid=', pizza_id) }catch(e){}
  const cart = loadCart()
  const existing = cart.find(c=>c.pizza_id === pizza_id)
  if(existing) existing.quantity += 1
  else cart.push({pizza_id, quantity:1})
  saveCart(cart)
  renderCart()
  if(typeof window.showToast === 'function'){
    try{ window.showToast('Added to cart') }catch(e){ console.log('[order.js] showToast threw', e) }
  } else { console.log('[order.js] showToast not available') }
}

function changeQty(pizza_id, delta){
  const cart = loadCart()
  const it = cart.find(c=>c.pizza_id===pizza_id)
  if(!it) return
  it.quantity += delta
  if(it.quantity <= 0){ const idx = cart.findIndex(c=>c.pizza_id===pizza_id); cart.splice(idx,1) }
  saveCart(cart)
  renderCart()
}

function removeItem(pizza_id){
  const cart = loadCart().filter(c=>c.pizza_id!==pizza_id)
  saveCart(cart)
  renderCart()
}

function initCart(){
  try{ console.log('[order.js] initCart start; PIZZAS keys=', Object.keys(window.PIZZAS||{}), 'storedCart=', localStorage.getItem(CART_KEY)) }catch(e){}
  // build a price/name map from server-rendered data OR from the .card elements on the page
  // If the server already provided window.PIZZAS (on /checkout), keep it. Otherwise, when .card elements exist (on /menu), build the map.
  if(document.querySelectorAll('.card').length > 0){
    window.PIZZAS = window.PIZZAS || {}
    document.querySelectorAll('.card').forEach(card=>{
      const pid = parseInt(card.dataset.pid)
      const price = parseFloat(card.dataset.price)
      const name = card.dataset.name || null
      if(pid) window.PIZZAS[pid] = { name: name || (`Pizza ${pid}`), price: price || 0 }
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
    // get pid from button dataset or from enclosing .card
    const pidAttr = btn.dataset && btn.dataset.pid ? btn.dataset.pid : (btn.closest ? (btn.closest('.card') && btn.closest('.card').dataset && btn.closest('.card').dataset.pid) : null)
    const pid = parseInt(pidAttr)
    if(isNaN(pid)){
      try{ console.warn('[order.js] add-to-cart clicked but pid missing or invalid', pidAttr) }catch(e){}
      return
    }
    addToCart(pid)
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
    try{ const saved = JSON.parse(localStorage.getItem(CUST_KEY) || '{}'); Object.keys(saved).forEach(k=>{ if(form[k]) form[k].value = saved[k] }) }catch(e){}
    ['name','email','phone','address','birthday','discount_code'].forEach(k=>{
      if(form[k]) form[k].addEventListener('input', ()=>{
        const obj = JSON.parse(localStorage.getItem(CUST_KEY) || '{}')
        obj[k]=form[k].value
        localStorage.setItem(CUST_KEY, JSON.stringify(obj))
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
        items: cart.map(i=>({pizza_id: i.pizza_id, quantity: i.quantity})),
        discount_code: form.discount_code.value || undefined
      }
      const res = await fetch('/orders', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)})
      const json = await res.json()
      const out = document.getElementById('order-result')
      if(res.status === 201){ out.innerText = `Order placed! id=${json.order_id}, total=${json.total}, delivery=${json.delivery_person}`; localStorage.removeItem(CART_KEY); renderCart() }
      else { out.innerText = 'Error: ' + (json.error || JSON.stringify(json)) }
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
