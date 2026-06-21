describe('CP-003 - Registro de cliente', () => {

  it('Debe registrar un cliente correctamente', () => {

    cy.visit('/registro/');

    cy.get('input[name="nombre"]').type('juan');
    cy.get('input[name="apellido"]').type('Rubiano');
    cy.get('input[name="email"]').type('juanes@gmail.com');
    cy.get('input[name="password"]').type('1028942721');
    cy.get('input[name="confirm"]').type('1028942721');

    cy.contains('Registrarse').click();

    cy.url().should('include', '/');

  });

});