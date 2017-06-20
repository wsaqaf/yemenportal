require "rails_helper"

describe Source do
  it { is_expected.to validate_presence_of(:link) }
  it { is_expected.to enumerize(:state).in(:valid, :incorrect_path, :incorrect_stucture, :not_full_info, :other) }

  describe "#facebook_page" do
    let(:fb_source) { build(:source, link: "https://www.facebook.com/ByRoR", source_type: :facebook) }
    let(:rss_source) { build(:source, link: "https://some_name/ByRoR", source_type: :rss) }

    it { expect(fb_source.facebook_page).to eql("ByRoR") }
    it { expect(rss_source.facebook_page).to be(nil) }
  end
end
