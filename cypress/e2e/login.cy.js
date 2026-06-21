describe('CP-001 - Inicio de sesión exitoso', () => {

  it('Login correcto', () => {

    cy.visit('https://barberiaragnarok.onrender.com/')

    cy.get('#email').type('admin@gmail.com')
    cy.get('#password').type('admin123')

    cy.get('button[type="submit"]').click()

    cy.url().should('include', '/dashboard')
  })

})