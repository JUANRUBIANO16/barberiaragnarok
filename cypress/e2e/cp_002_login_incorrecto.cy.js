describe('CP-002 - Login con contraseña incorrecta', () => {

  it('Debe mostrar error y no permitir acceso', () => {

    // Ir al login (ruta base)
    cy.visit('/');

    // Ingresar credenciales
    cy.get('input[name="email"]').type('admin@gmail.com');
    cy.get('input[name="password"]').type('123');

    // Iniciar sesión
    cy.contains('Iniciar sesión').click();

    // Validar mensaje de error
   cy.contains('Contraseña incorrecta', { timeout: 8000 })
  .should('be.visible');

    // Validar que no se haya autenticado
    cy.url().should('include', '/');
  });

});