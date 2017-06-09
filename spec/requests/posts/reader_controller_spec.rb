require "rails_helper"

describe Posts::ReaderController, type: :request do
  describe "#show" do
    let(:post) { create :post, state: "pending" }
    let(:do_request) { get "/post/#{post.id}/reader" }

    it "post infor" do
      do_request

      expect(response).to have_http_status(:ok)
    end
  end
end
