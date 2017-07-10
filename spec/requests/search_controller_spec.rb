require "rails_helper"

describe SearchController, type: :request do
  describe "#index" do
    let(:post) { create(:post, title: "test name") }

    context "without params" do
      let(:do_request) { get "/search", params: { search_form: { search_text: "test" } } }

      it "show a main page" do
        do_request

        expect(response).to have_http_status(:ok)
      end
    end
  end
end
