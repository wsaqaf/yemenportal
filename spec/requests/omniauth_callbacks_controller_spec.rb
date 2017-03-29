require "rails_helper"

describe OmniauthCallbacksController, type: :request do
  describe "#failure" do
    let(:do_request) { get "/users/auth/twitter/callback", auth: { a: 2 } }

    it "redirect to sources list" do
      do_request

      expect(response.status).to eq 302
      expect(response).to redirect_to(root_path)
    end
  end
end
