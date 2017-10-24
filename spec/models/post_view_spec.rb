require "rails_helper"

describe PostView do
  describe "relations" do
    it { is_expected.to belong_to(:post).counter_cache(:post_views_count).touch(true) }
    it { is_expected.to belong_to(:user) }
  end
end
