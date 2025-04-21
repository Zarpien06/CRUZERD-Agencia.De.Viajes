// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar componentes de Bootstrap
  initBootstrapComponents();
  
  // Inicializar validación de formularios
  initFormValidation();
  
  // Inicializar datepickers
  initDatepickers();
  
  // Inicializar contadores de pasajeros
  initPassengerCounters();
  
  // Inicializar cambios entre tabs del buscador
  initSearchTabs();
  
  // Inicializar animaciones scroll
  initScrollAnimations();
  
  // Inicializar tooltips
  initTooltips();
  
  // Inicializar interacciones modales
  initModalInteractions();
});

// Inicializar componentes de Bootstrap
function initBootstrapComponents() {
  // Activar todos los tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
  });
  
  // Activar todos los popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
      return new bootstrap.Popover(popoverTriggerEl);
  });
}

// Inicializar datepickers
function initDatepickers() {
  // Esta función se usaría si implementamos un plugin de datepicker como flatpickr
  // Por ahora usamos los inputs nativos de tipo date de HTML5
  
  // Ejemplo con flatpickr si se desea implementar
  /*
  if(document.getElementById('departure-date')) {
      flatpickr("#departure-date", {
          minDate: "today",
          dateFormat: "d/m/Y",
          defaultDate: "10/05/2025"
      });
      
      flatpickr("#return-date", {
          minDate: "today",
          dateFormat: "d/m/Y",
          defaultDate: "17/05/2025"
      });
  }
  */
  
  // Por ahora, solo establecemos las fechas por defecto en los inputs nativos
  const departureInput = document.getElementById('departure-date');
  const returnInput = document.getElementById('return-date');
  
  if(departureInput && returnInput) {
      // Establecer fechas por defecto (10/05/2025 y 17/05/2025)
      const currentYear = new Date().getFullYear();
      departureInput.value = '2025-05-10';
      returnInput.value = '2025-05-17';
      
      // Habilitar/deshabilitar fecha de regreso según selección
      const tripTypeRadios = document.querySelectorAll('input[name="trip-type"]');
      tripTypeRadios.forEach(radio => {
          radio.addEventListener('change', function() {
              if (this.value === 'one-way') {
                  returnInput.disabled = true;
                  returnInput.value = '';
              } else {
                  returnInput.disabled = false;
                  returnInput.value = '2025-05-17';
              }
          });
      });
  }
}

// Inicializar contadores de pasajeros
function initPassengerCounters() {
  const decrementButtons = document.querySelectorAll('.passenger-decrement');
  const incrementButtons = document.querySelectorAll('.passenger-increment');
  const passengerInputs = document.querySelectorAll('.passenger-count');
  const totalPassengersElement = document.getElementById('total-passengers');
  
  // Función para actualizar el total de pasajeros
  function updateTotalPassengers() {
      let total = 0;
      passengerInputs.forEach(input => {
          total += parseInt(input.value);
      });
      
      if(totalPassengersElement) {
          const passengerText = total === 1 ? 'pasajero' : 'pasajeros';
          totalPassengersElement.textContent = `${total} ${passengerText}`;
      }
  }
  
  // Asignar eventos a los botones de decremento
  decrementButtons.forEach(button => {
      button.addEventListener('click', function() {
          const input = this.nextElementSibling;
          let value = parseInt(input.value);
          
          // Verificar el mínimo según el tipo de pasajero
          let minValue = 0;
          if(input.id === 'adults') {
              minValue = 1; // Al menos 1 adulto
          }
          
          if(value > minValue) {
              input.value = value - 1;
              updateTotalPassengers();
          }
      });
  });
  
  // Asignar eventos a los botones de incremento
  incrementButtons.forEach(button => {
      button.addEventListener('click', function() {
          const input = this.previousElementSibling;
          let value = parseInt(input.value);
          
          // Verificar el máximo según el tipo de pasajero
          let maxValue = 9;
          
          if(value < maxValue) {
              input.value = value + 1;
              updateTotalPassengers();
          }
      });
  });
  
  // Inicializar el contador total
  updateTotalPassengers();
}

// Inicializar tabs del buscador
function initSearchTabs() {
  const searchTabs = document.querySelectorAll('.search-nav .nav-link');
  const searchForms = document.querySelectorAll('.search-content .tab-pane');
  
  searchTabs.forEach(tab => {
      tab.addEventListener('click', function(e) {
          e.preventDefault();
          
          // Remover clase active de todos los tabs
          searchTabs.forEach(t => t.classList.remove('active'));
          
          // Añadir clase active al tab clickeado
          this.classList.add('active');
          
          // Mostrar el formulario correspondiente
          const targetId = this.getAttribute('data-bs-target').substring(1);
          
          searchForms.forEach(form => {
              if(form.id === targetId) {
                  form.classList.add('active', 'show');
              } else {
                  form.classList.remove('active', 'show');
              }
          });
      });
  });
}

// Inicializar validación de formularios
function initFormValidation() {
  const forms = document.querySelectorAll('.needs-validation');
  
  Array.from(forms).forEach(form => {
      form.addEventListener('submit', event => {
          if (!form.checkValidity()) {
              event.preventDefault();
              event.stopPropagation();
          } else {
              // Si el formulario es válido, mostrar mensaje de carga
              const submitBtn = form.querySelector('button[type="submit"]');
              if(submitBtn) {
                  const originalText = submitBtn.innerHTML;
                  submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';
                  
                  // Restaurar el texto original después de 2 segundos (simulación)
                  setTimeout(() => {
                      submitBtn.innerHTML = originalText;
                  }, 2000);
              }
          }
          
          form.classList.add('was-validated');
          event.preventDefault(); // Prevenir envío real en este ejemplo
      }, false);
  });
}

// Inicializar animaciones al hacer scroll
function initScrollAnimations() {
  // Detectar elementos para animar
  const animatedElements = document.querySelectorAll('.animate-on-scroll');
  
  // Función para verificar si un elemento está en el viewport
  function isElementInViewport(el) {
      const rect = el.getBoundingClientRect();
      return (
          rect.top <= (window.innerHeight || document.documentElement.clientHeight) * 0.8 &&
          rect.bottom >= 0
      );
  }
  
  // Función para animar elementos visibles
  function animateVisibleElements() {
      animatedElements.forEach(element => {
          if(isElementInViewport(element) && !element.classList.contains('animated')) {
              element.classList.add('animated');
          }
      });
  }
  
  // Ejecutar en carga y scroll
  animateVisibleElements();
  window.addEventListener('scroll', animateVisibleElements);
}

// Inicializar tooltips
function initTooltips() {
  // Ya inicializado en initBootstrapComponents()
  // Esta función se mantiene por si se necesitan tooltips personalizados
}

// Funcionalidad para el intercambio de origen y destino
function swapOriginDestination() {
  const originInput = document.getElementById('flight-origin');
  const destinationInput = document.getElementById('flight-destination');
  
  if(originInput && destinationInput) {
      const originValue = originInput.value;
      originInput.value = destinationInput.value;
      destinationInput.value = originValue;
  }
}

// Funcionalidad para el menú de pasajeros desplegable
document.addEventListener('click', function(e) {
  const passengerDropdown = document.getElementById('passenger-dropdown');
  const passengerToggle = document.getElementById('passenger-toggle');
  
  if(!passengerDropdown || !passengerToggle) return;
  
  if(passengerToggle.contains(e.target)) {
      // Si se hizo clic en el botón toggle
      passengerDropdown.classList.toggle('show');
  } else if(!passengerDropdown.contains(e.target)) {
      // Si se hizo clic fuera del dropdown
      passengerDropdown.classList.remove('show');
  }
});

// Manejar click en botón "Ver ofertas"
const seeOffersBtn = document.querySelector('.btn-see-offers');
if(seeOffersBtn) {
  seeOffersBtn.addEventListener('click', function(e) {
      e.preventDefault();
      // Desplazarse suavemente a la sección de ofertas
      document.querySelector('.promo-section').scrollIntoView({ 
          behavior: 'smooth' 
      });
  });
}

// Mostrar mensaje de newsletter
const newsletterForm = document.querySelector('.newsletter-section form');
if(newsletterForm) {
  newsletterForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const emailInput = this.querySelector('input[type="email"]');
      if(emailInput && emailInput.value) {
          // Ocultar el formulario
          this.style.display = 'none';
          
          // Mostrar mensaje de confirmación
          const thankYouMessage = document.createElement('div');
          thankYouMessage.className = 'alert alert-success mt-4';
          thankYouMessage.innerHTML = '<h4>¡Gracias por suscribirse!</h4><p>Pronto recibirá nuestras mejores ofertas en su correo.</p>';
          
          this.parentNode.appendChild(thankYouMessage);
      }
  });
}

// Detectar cambios en la barra de navegación al hacer scroll
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar');
  if(!navbar) return;
  
  if(window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled');
  } else {
      navbar.classList.remove('navbar-scrolled');
  }
});

// Función para contar regresivamente las ofertas
function startCountdown() {
  const countdownElements = document.querySelectorAll('.countdown');
  
  countdownElements.forEach(el => {
      // Establecer tiempo final aleatorio (entre 1 y 24 horas)
      const hours = Math.floor(Math.random() * 23) + 1;
      const minutes = Math.floor(Math.random() * 59);
      const seconds = Math.floor(Math.random() * 59);
      
      let totalSeconds = hours * 3600 + minutes * 60 + seconds;
      
      // Actualizar cada segundo
      const interval = setInterval(() => {
          totalSeconds--;
          
          if(totalSeconds <= 0) {
              clearInterval(interval);
              el.innerHTML = '¡Oferta terminada!';
              return;
          }
          
          const hoursLeft = Math.floor(totalSeconds / 3600);
          const minutesLeft = Math.floor((totalSeconds % 3600) / 60);
          const secondsLeft = totalSeconds % 60;
          
          el.innerHTML = `${hoursLeft.toString().padStart(2, '0')}:${minutesLeft.toString().padStart(2, '0')}:${secondsLeft.toString().padStart(2, '0')}`;
      }, 1000);
  });
}

// Iniciar countdown si hay elementos
if(document.querySelector('.countdown')) {
  startCountdown();
}


// Interacciones de los modales
function initModalInteractions() {
// Switch entre modales de login y registro
const loginToRegisterLinks = document.querySelectorAll('[data-bs-target="#registerModal"][data-bs-dismiss="modal"]');
const registerToLoginLinks = document.querySelectorAll('[data-bs-target="#loginModal"][data-bs-dismiss="modal"]');

loginToRegisterLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
        if(loginModal) {
            loginModal.hide();
            setTimeout(() => {
                const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
                registerModal.show();
            }, 500);
        }
    });
});

registerToLoginLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
        if(registerModal) {
            registerModal.hide();
            setTimeout(() => {
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            }, 500);
        }
    });
});
}

// login y register

document.addEventListener('DOMContentLoaded', function() {
// Referencias a elementos del DOM
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const passwordInputs = document.querySelectorAll('input[type="password"]');
const toggleButtons = document.querySelectorAll('.toggle-password');
const rolSelect = document.getElementById('rol');
const proveedorFields = document.getElementById('proveedorFields');
const registerPassword = document.getElementById('registerPassword');
const passwordStrengthBar = document.querySelector('#passwordStrength .progress-bar');

document.addEventListener("DOMContentLoaded", function () {
  // Ocultar todos los spinners al inicio
  document.querySelectorAll('.spinner-border').forEach(spinner => {
      spinner.style.display = 'none';
  });

  // Mostrar el spinner cuando se envía el formulario de login
  const loginForm = document.getElementById("loginForm");
  const loginSpinner = document.getElementById("loginSpinner");

  if (loginForm) {
      loginForm.addEventListener("submit", function () {
          if (loginSpinner) {
              loginSpinner.style.display = 'inline-block';
          }
      });
  }
});

/*
 * Funcionalidad de mostrar/ocultar contraseña
 */
toggleButtons.forEach(button => {
  button.addEventListener('click', function() {
    const passwordInput = this.previousElementSibling;
    const icon = this.querySelector('i');
    
    // Cambiar tipo de input
    if (passwordInput.type === 'password') {
      passwordInput.type = 'text';
      icon.classList.remove('fa-eye');
      icon.classList.add('fa-eye-slash');
    } else {
      passwordInput.type = 'password';
      icon.classList.remove('fa-eye-slash');
      icon.classList.add('fa-eye');
    }
  });
});

/*
 * Mostrar campos específicos según el rol seleccionado
 */
if (rolSelect) {
  rolSelect.addEventListener('change', function() {
    if (this.value === 'proveedor') {
      proveedorFields.style.display = 'block';
      
      // Hacer campos obligatorios
      document.getElementById('nombre_empresa').required = true;
      document.getElementById('tipo_proveedor').required = true;
    } else {
      proveedorFields.style.display = 'none';
      
      // Quitar obligatoriedad
      document.getElementById('nombre_empresa').required = false;
      document.getElementById('tipo_proveedor').required = false;
    }
  });
}

/*
 * Medidor de fortaleza de contraseña
 */
if (registerPassword) {
  registerPassword.addEventListener('input', function() {
    const password = this.value;
    let strength = 0;
    
    // Criterios de fortaleza
    if (password.length >= 8) strength += 25;
    if (password.match(/[A-Z]/)) strength += 25;
    if (password.match(/[0-9]/)) strength += 25;
    if (password.match(/[^a-zA-Z0-9]/)) strength += 25;
    
    // Actualizar barra de progreso
    passwordStrengthBar.style.width = strength + '%';
    
    // Cambiar color según fortaleza
    if (strength <= 25) {
      passwordStrengthBar.className = 'progress-bar bg-danger';
    } else if (strength <= 50) {
      passwordStrengthBar.className = 'progress-bar bg-warning';
    } else if (strength <= 75) {
      passwordStrengthBar.className = 'progress-bar bg-info';
    } else {
      passwordStrengthBar.className = 'progress-bar bg-success';
    }
  });
}




// Validación y envío del formulario de login
// Función mejorada para manejar el login
if (loginForm) {
loginForm.addEventListener('submit', function (e) {
  e.preventDefault();

  const submitButton = this.querySelector('button[type="submit"]');
  const spinner = submitButton.querySelector('.spinner-border');
  const alertBox = document.getElementById('loginAlert');

  if (!this.checkValidity()) {
    e.stopPropagation();
    this.classList.add('was-validated');
    return;
  }

  // Mostrar spinner
  spinner.style.display = 'inline-block';
  submitButton.disabled = true;

  // Recopilar datos del formulario
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;

  // Verificar que ambos campos existan
  if (!email || !password) {
    spinner.style.display = 'none';
    submitButton.disabled = false;
    alertBox.textContent = 'Por favor, complete todos los campos';
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert-danger');
    return;
  }

  // Crear objeto FormData
  const formData = new FormData();
  formData.append('email', email);
  formData.append('password', password);

  // Enviar la solicitud al servidor
  fetch('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: new URLSearchParams(formData).toString()
  })
  .then(response => {
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.message || 'Error en la solicitud: ' + response.status);
      }).catch(err => {
        throw new Error('Respuesta no válida del servidor: ' + response.status);
      });
    }

    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return response.json();
    } else {
      return { success: true, redirect: response.url };
    }
  })
  .then(data => {
    spinner.style.display = 'none';
    submitButton.disabled = false;

    if (data.success) {
      alertBox.textContent = data.message || 'Inicio de sesión exitoso';
      alertBox.classList.remove('d-none', 'alert-danger');
      alertBox.classList.add('alert-success');

      setTimeout(() => {
        window.location.href = data.redirect || '/';
      }, 1000);
    } else {
      alertBox.textContent = data.message || 'Error al iniciar sesión';
      alertBox.classList.remove('d-none', 'alert-success');
      alertBox.classList.add('alert-danger');
    }
  })
  .catch(error => {
    spinner.style.display = 'none';
    submitButton.disabled = false;
    alertBox.textContent = 'Error de conexión. Por favor, inténtelo nuevamente.';
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert-danger');
    console.error('Error:', error);
  });
});
}



/*
* Validación y envío del formulario de registro
*/// Función mejorada para manejar el registro
if (registerForm) {
registerForm.addEventListener('submit', function(e) {
  e.preventDefault();
  
  const submitButton = this.querySelector('button[type="submit"]');
  const spinner = submitButton.querySelector('.spinner-border');
  const alertBox = document.getElementById('registerAlert');
  
  // Validar formulario
  if (!this.checkValidity()) {
    e.stopPropagation();
    this.classList.add('was-validated');
    return;
  }
  
  // Obtener valores del formulario
  const email = document.getElementById('registerEmail').value;
  const nombre = document.getElementById('nombre').value;
  const password = document.getElementById('registerPassword').value;
  const confirmPassword = document.getElementById('confirm_password').value;
  const rol = document.getElementById('rol').value;
  
  // Validar campos obligatorios
  if (!email || !nombre || !password || !confirmPassword || !rol) {
    alertBox.textContent = 'Por favor, complete todos los campos obligatorios';
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert-danger');
    return;
  }
  
  // Validar que las contraseñas coincidan
  if (password !== confirmPassword) {
    alertBox.textContent = 'Las contraseñas no coinciden';
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert-danger');
    return;
  }
  
  // Mostrar spinner durante la carga
  spinner.style.display = 'inline-block';
  submitButton.disabled = true;
  
  // Crear objeto FormData
  const formData = new FormData();
  formData.append('email', email);
  formData.append('nombre', nombre);
  formData.append('password', password);
  formData.append('confirm_password', confirmPassword);
  formData.append('rol', rol);
  
  // Si es proveedor, añadir campos adicionales
  if (rol === 'proveedor') {
    const nombreEmpresa = document.getElementById('nombre_empresa').value;
    const tipoProveedor = document.getElementById('tipo_proveedor').value;
    
    if (!nombreEmpresa || !tipoProveedor) {
      spinner.style.display = 'none';
      submitButton.disabled = false;
      alertBox.textContent = 'Complete los campos específicos para proveedores';
      alertBox.classList.remove('d-none', 'alert-success');
      alertBox.classList.add('alert-danger');
      return;
    }
    
    formData.append('nombre_empresa', nombreEmpresa);
    formData.append('tipo_proveedor', tipoProveedor);
  }
  
  // Enviar datos al servidor
  fetch('/register', {
    method: 'POST',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams(formData).toString()
  })
  .then(response => {
    // Validar la respuesta
    if (!response.ok) {
      return response.json().then(data => {
        throw new Error(data.message || 'Error en la solicitud: ' + response.status);
      }).catch(err => {
        throw new Error('Error de red o respuesta no válida: ' + response.status);
      });
    }
    
    // Intentar obtener JSON
    const contentType = response.headers.get("content-type");
    if (contentType && contentType.includes("application/json")) {
      return response.json();
    } else {
      // Si no es JSON, podría ser una redirección
      return { success: true, redirect: response.url };
    }
  })
  .then(data => {
    spinner.style.display = 'none';
    submitButton.disabled = false;
    
    if (data.success) {
      // Mostrar mensaje de éxito
      alertBox.textContent = data.message || '¡Registro exitoso! Redirigiendo al inicio de sesión...';
      alertBox.classList.remove('d-none', 'alert-danger');
      alertBox.classList.add('alert-success');
      
      // Redirigir después de un momento
      setTimeout(() => {
        // Cerrar modal de registro y abrir el de login
        const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
        if (registerModal) {
          registerModal.hide();
        }
        
        // Limpiar formulario
        this.reset();
        
        // Mostrar modal de login con mensaje
        setTimeout(() => {
          const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
          const loginAlertBox = document.getElementById('loginAlert');
          
          if (loginAlertBox) {
            loginAlertBox.textContent = '¡Registro exitoso! Ya puede iniciar sesión.';
            loginAlertBox.classList.remove('d-none', 'alert-danger');
            loginAlertBox.classList.add('alert-success');
          }
          
          if (loginModal) {
            loginModal.show();
          } else {
            window.location.href = data.redirect || '/';
          }
        }, 500);
      }, 1500);
    } else {
      // Mostrar mensaje de error
      alertBox.textContent = data.message || 'Error al crear cuenta. Por favor, inténtelo nuevamente.';
      alertBox.classList.remove('d-none', 'alert-success');
      alertBox.classList.add('alert-danger');
    }
  })
  .catch(error => {
    spinner.style.display = 'none';
    submitButton.disabled = false;
    
    alertBox.textContent = 'Error de conexión. Por favor, inténtelo nuevamente.';
    alertBox.classList.remove('d-none', 'alert-success');
    alertBox.classList.add('alert-danger');
    console.error('Error:', error);
  });
});
}






/*
 * Limpiar alertas al cerrar un modal
 */
const modals = document.querySelectorAll('.modal');
modals.forEach(modal => {
  modal.addEventListener('hidden.bs.modal', function() {
    const alertBox = this.querySelector('.alert');
    if (alertBox) {
      alertBox.classList.add('d-none');
      alertBox.classList.remove('alert-danger', 'alert-success');
      alertBox.textContent = '';
    }
    
    // Resetear formularios
    const form = this.querySelector('form');
    if (form) {
      form.reset();
      form.classList.remove('was-validated');
    }
    
    // Ocultar spinners
    const spinner = this.querySelector('.spinner-border');
    if (spinner) {
      spinner.style.display = 'none';
    }
    
    // Habilitar botones
    const submitButton = this.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = false;
    }
    
    // Reiniciar barra de fortaleza de contraseña
    if (this.id === 'registerModal' && passwordStrengthBar) {
      passwordStrengthBar.style.width = '0%';
      passwordStrengthBar.className = 'progress-bar';
    }
    
    // Ocultar campos específicos
    if (this.id === 'registerModal' && proveedorFields) {
      proveedorFields.style.display = 'none';
    }
  });
});

/*
 * Asegurarse de que el evento 'hidden.bs.modal' se active correctamente
 */
// Forzar la inicialización adecuada de los modales de Bootstrap
document.querySelectorAll('[data-bs-toggle="modal"]').forEach(element => {
  element.addEventListener('click', function(e) {
    // Si hay un modal abierto, cerrarlo correctamente
    const openModals = document.querySelectorAll('.modal.show');
    openModals.forEach(modal => {
      const modalInstance = bootstrap.Modal.getInstance(modal);
      if (modalInstance) {
        modalInstance.hide();
      }
    });
  });
});

/*
 * Cambiar tipo de campo de contraseña al iniciar
 * para evitar autocompletado indeseado en algunos navegadores
 */
passwordInputs.forEach(input => {
  input.type = 'password';
});

/*
 * Inicializar tooltips si se usan
 */
if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
  const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
  tooltips.forEach(tooltip => {
    new bootstrap.Tooltip(tooltip);
  });
}
});


