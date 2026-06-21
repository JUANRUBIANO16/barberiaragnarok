describe('CP-007 - Precio inválido en servicios', () => {

  it('Debe bloquear creación con precio inválido', () => {

    cy.login();

    cy.visit('/servicios/');

    // abrir modal (FIABLE)
    cy.get('[data-cy="btn-open-servicio"]')
      .should('be.visible')
      .click();

    // modal visible
    cy.get('#addEmployeeModal')
      .should('be.visible');

    // llenar formulario
    cy.get('[data-cy="input-nombre"]').type('Corte');
    cy.get('[data-cy="input-precio"]').type('-67000');
    cy.get('[data-cy="input-descripcion"]').type('Test servicio');

    // guardar
    cy.get('[data-cy="btn-guardar-servicio"]').click();

    // validación backend (Django message)
    cy.get('.alert', { timeout: 10000 })
      .should('be.visible')
      .and('contain.text', 'precio');

  });

});