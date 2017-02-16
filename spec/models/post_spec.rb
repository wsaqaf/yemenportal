require 'rails_helper'

describe Post do
  %i(title pub_date link).each do |field|
    it { should validate_presence_of(field) }
  end
end
