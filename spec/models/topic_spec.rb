require "rails_helper"

describe Topic do
  describe "relations" do
    it { is_expected.to belong_to(:main_post).class_name("Post") }
    it { is_expected.to have_many(:posts).dependent(:destroy) }
  end
end
