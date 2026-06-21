describe('CP-006 - Usuario con correo duplicado', () => {

  it('Debe rechazar el registro de un correo ya existente', () => {

    // ======================
    // LOGIN
    // ======================
    cy.login();

    // ======================
    // IR A USUARIOS
    // ======================
    cy.visit('/usuarios/');

    // ======================
    // ABRIR MODAL
    // ======================
    cy.contains('Agregar Usuario')
      .click({ force: true });

    // ======================
    // ESPERAR MODAL REALMENTE LISTO
    // ======================
    cy.get('#addEmployeeModal')
      .should('be.visible');

    cy.get('#addEmployeeModal input[name="nombre"]')
      .should('be.visible')
      .type('Juan');

    cy.get('#addEmployeeModal input[name="apellido"]')
      .should('be.visible')
      .type('Perez');

    cy.get('#addEmployeeModal input[name="email"]')
      .should('be.visible')
      .type('admin@gmail.com'); // duplicado

    cy.get('#addEmployeeModal input[name="password"]')
      .should('be.visible')
      .type('123456');

    cy.get('#addEmployeeModal select[name="tipo_usuario"]')
      .should('be.visible')
      .select('barbero');

    // ======================
    // GUARDAR
    // ======================
    cy.contains('Guardar')
      .click({ force: true });

    // ======================
    // VALIDAR MENSAJE
    // ======================
    cy.get('.alert, .custom-alert', { timeout: 10000 })
      .should('be.visible')
      .invoke('text')
      .then((text) => {
        expect(text.toLowerCase()).to.include('correo');
      });

  });

});