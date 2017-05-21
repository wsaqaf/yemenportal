require "rails_helper"

describe PostAssociation do
  it { is_expected.to belong_to(:dependent_post).class_name("Post") }
  it { is_expected.to belong_to(:main_post).class_name("Post") }
end
