Feature: The arguments feed
  Scenario: User wants to view argument feed
    Given an argument exists
    And I am on the homepage
    Then I should see "Number of comments:"

  Scenario: Users wants to add an argument
    Given I am on the homepage
    When I click "+ Add Argument"
    And I fill "arg_title" in with "test_title"
    And I fill "statement" in with "test_statement"
    And I press "submit"
    Then I should see "Argument created."
