require "rails_helper"

describe Api::SourcesController, type: :request do
  let(:user) { build :user }

  describe "#update" do
    let(:source) { create :source }
    let(:posts_fetcher_job) { double }
    let(:do_request) do
      put "/api/sources/#{source.id}", params: { link: "http://ddd1234.com" }
    end
    let(:do_bad_request) do
      put "/api/sources/#{source.id}", params: { link: "" }
    end

    it "source params" do
      sign_in user

      do_request
      expect(Source.find(source.id).link).to eql("http://ddd1234.com")
    end

    it "source fails" do
      sign_in user
      do_bad_request

      expect(response.status).to eq 400
    end
  end
end
