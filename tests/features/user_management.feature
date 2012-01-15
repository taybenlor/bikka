Feature: Basic user management
  Background:
    Given I am on the homepage

  Scenario: User logs in
    Given a user with name "bob" and password "bob" exists
    When I go to the login page
    And I fill "username" in with "bob"
    And I fill "password" in with "bob"
    And I press "submit_login"
    Then I should see "Login successful."

  Scenario: User logs out
    Given a user with name "bobout" and password "bobout" exists
    When I go to the login page
    And I fill "username" in with "bobout"
    And I fill "password" in with "bobout"
    And I press "submit_login"
    When I go to the logout page
    Then I should see "You have been logged out."
    
  Scenario: User registers
    When I click "Register"
    And I fill "newusername" in with "test_samtar"
    And I fill "email" in with "test_samtar@example.com"
    And I fill "newpassword" in with "test_samtar"
    And I fill "confpassword" in with "test_samtar"
    And I press "submit_register"
    Then I should see "Thankyou for registering."

#  Scenario: User views their profile
    #Given I am logged in as "user_samtar"
    #When I click "test_samtar"
    #Then I should see "User name: test_samtar"
    #And I should see "First name: test_sam"
    #And I should see "Last name: test_tar"
    #And I should see "DOB: 21/08/86"
