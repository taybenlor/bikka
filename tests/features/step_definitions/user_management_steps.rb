require 'watir-webdriver'
require 'rspec/expectations'
require 'sqlite3'

#Given /^I am on the homepage$/ do
  #@browser ||= Watir::Browser.new :ff
  #@browser.goto "http://localhost:8888"
#end

Given /^a user with name "([^"]+)" and password "([^"]+)" exists$/ do |username, password|
  @username = username
  db = SQLite3::Database.new 'database.sqlitedb'
  hashpw = Digest::MD5.hexdigest(password)
  db.execute "insert into users (username, password, email) values ('#{username}', '#{hashpw}', 'test_email@example.com')"
end

When /^I go to the login page$/ do
  @browser.goto "http://localhost:8888/login"
end

When /^I go to the logout page$/ do
  @browser.goto "http://localhost:8888/logout"
end

When /^I log in as "([^"]+)" with password "([^"]+)"$/ do |username, password|
  Given "I go to the login page"
  @browser.text_field(:username).set username
  @browser.text_field(:password).set password
  @browser.button(:name => "submit").click
end

#Then /^I should see my profile page$/ do

#end

#When /^I go to the logout page$/ do
  #@browser.goto "/logout"
#end

#After do
  #@browser.close
#end

When /^I click "([^"]*)"$/ do |link_text|
  @browser.link(:text, link_text).click
end

When /^I fill "([^"]*)" in with "([^"]*)"$/ do |form_element, value|
  @browser.text_field(:name, form_element).set value
end

When /^I press "([^"]*)"$/ do |button_name|
  @browser.button(:name, button_name).click
end

#Then /^I should see "([^"]*)"$/ do |text|
  #@browser.text.include?(text).should be_true
#end
