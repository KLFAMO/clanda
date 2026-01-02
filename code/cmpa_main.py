from settings import TOCK_DATA_PATH
import cmpa

def main():
    metas = cmpa.discover_comparators(TOCK_DATA_PATH)
    print(metas)
    metas = [cmpa.load_yaml_into_meta(m) for m in metas]
    g = cmpa.build_connection_graph(metas)
    print(cmpa.report_graph(g))

if __name__ == "__main__":
    main()
